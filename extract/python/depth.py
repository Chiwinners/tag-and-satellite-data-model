#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import logging
from pathlib import Path
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
import earthaccess as ea
from tqdm import tqdm

with open('downloads/depth/nasa.txt', 'r') as file:
    DEFAULT_URLS = file.read().splitlines()

def parse_args():
    p = argparse.ArgumentParser(
        description="Descarga paralela con earthaccess (token EDL), reintentos, barras de progreso y logs."
    )
    p.add_argument("-u","--urls-file", help="Archivo de texto con una URL por línea.")
    p.add_argument("-o","--outdir", default="downloads", help="Directorio de salida (default: downloads)")
    p.add_argument("-w","--workers", type=int, default=os.cpu_count() or 4, help="Descargas en paralelo (default: CPUs)")
    p.add_argument("--logical-retries", type=int, default=3, help="Reintentos lógicos por archivo (default: 3)")
    p.add_argument("--debug", action="store_true", help="Activa logging DEBUG detallado")
    return p.parse_args()

def setup_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S"
    )

def fname(url: str) -> str:
    name = urlsplit(url).path.rsplit("/",1)[-1].split("?",1)[0]
    return name or "download.bin"

def diagnose_auth_issue(e: Exception) -> str:
    msg = str(e)
    # pistas típicas cuando falta autorización URS o cookies válidas
    if "403" in msg or "401" in msg or "Forbidden" in msg or "Unauthorized" in msg:
        return ("Falta autorizar la aplicación/endpoint en Earthdata (URS). "
                "Abre la URL en el navegador autenticado y pulsa 'Authorize'.")
    return msg

def get_expected_size(fs, url: str):
    """
    Usa fsspec https session de earthaccess para consultar metadata del recurso.
    Si el servidor no soporta HEAD/info, devuelve None.
    """
    try:
        info = fs.info(url)  # puede lanzar
        size = info.get("size")
        logging.debug(f"[HEAD] {url} -> size={size}, info={info}")
        return int(size) if size is not None else None
    except Exception as e:
        logging.debug(f"[HEAD] No se pudo obtener tamaño de {url}: {e}")
        return None

def download_one(fs, url: str, outdir: Path, position: int, logical_retries: int = 3):
    """
    Descarga usando exclusivamente earthaccess.get_fsspec_https_session() (sin requests directo).
    Devuelve (url, ok, msg_error).
    """
    name = fname(url)
    dest = outdir / name
    tmp = outdir / (name + ".part")

    expected = get_expected_size(fs, url)  # None si no se conoce

    last_err = ""
    for k in range(1, logical_retries + 1):
        logging.debug(f"[{name}] intento {k}/{logical_retries} - inicio")
        try:
            if tmp.exists():
                tmp.unlink(missing_ok=True)

            # Abrimos en binario con fsspec https (autenticado por earthaccess)
            with fs.open(url, mode="rb") as r, open(tmp, "wb") as w, tqdm(
                total=expected, unit="B", unit_scale=True, unit_divisor=1024,
                desc=name, position=position, leave=True
            ) as bar:
                # Leemos en chunks
                chunk = 1024 * 1024
                while True:
                    data = r.read(chunk)
                    if not data:
                        break
                    w.write(data)
                    bar.update(len(data))

            # Validación por tamaño si conocemos expected
            if expected is not None and tmp.stat().st_size != expected:
                raise IOError(f"Tamaño descargado {tmp.stat().st_size} != esperado {expected}")

            tmp.replace(dest)
            logging.info(f"[OK] {name} -> {dest}")
            return (url, True, "")
        except Exception as e:
            # Diagnóstico y backoff
            diag = diagnose_auth_issue(e)
            last_err = f"[intento {k}/{logical_retries}] {diag}"
            logging.warning(f"[WARN] {name}: {last_err}")
            if k < logical_retries:
                sleep_s = min(5, 2 ** (k - 1))
                logging.debug(f"[{name}] backoff {sleep_s}s")
                time.sleep(sleep_s)

    return (url, False, last_err)

def main():
    args = parse_args()
    setup_logging(args.debug)

    # 1) Cargar .env
    load_dotenv()
    token_present = bool(os.getenv("EARTHDATA_TOKEN"))
    logging.info(f"EARTHDATA_TOKEN presente: {token_present}")
    if not token_present:
        logging.error("No se encontró EARTHDATA_TOKEN en el entorno (.env).")
        sys.exit(1)

    # 2) Login usando token del entorno (estrategia environment)
    logging.info("Haciendo login con earthaccess (strategy=environment)...")
    ea.login(strategy="environment")  # usa EARTHDATA_TOKEN del entorno
    logging.info("Login OK.")

    # 3) Sesión fsspec HTTPS autenticada (para abrir URLs directas)
    fs = ea.get_fsspec_https_session()
    logging.debug(f"fsspec fs creado: {fs}")

    # 4) Leer URLs
    if args.urls_file:
        with open(args.urls_file, "r", encoding="utf-8") as fh:
            urls = [ln.strip() for ln in fh if ln.strip() and not ln.strip().startswith("#")]
    else:
        urls = DEFAULT_URLS
    logging.info(f"Total de URLs a procesar: {len(urls)}")

    if not urls:
        logging.error("No hay URLs para descargar.")
        sys.exit(1)

    # 5) Preparar salida
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    logging.debug(f"Directorio de salida: {outdir.resolve()}")

    # 6) Paralelismo
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(download_one, fs, u, outdir, i, args.logical_retries) for i, u in enumerate(urls)]
        for f in as_completed(futs):
            url, ok, msg = f.result()
            if not ok:
                failures.append((url, msg))

    # 7) Resumen
    print("\nResumen:")
    print(f"  Total: {len(urls)}")
    print(f"  Exitosas: {len(urls) - len(failures)}")
    print(f"  Fallidas: {len(failures)}")
    if failures:
        print("\nDescargas fallidas:")
        for u, m in failures:
            print(f"- {u}")
            if m:
                print(f"  Motivo: {m}")
        print("\nSi aparece el mensaje de autorización URS:")
        print("  1) Abre cualquiera de las URLs en tu navegador autenticado en Earthdata.")
        print("  2) Pulsa 'Authorize' para el endpoint/app (paso único).")
        print("  3) Ejecuta de nuevo el script.")

if __name__ == "__main__":
    main()
