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


DEFAULT_URLS = [
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T190001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T185501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T185001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T172501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T172001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T171501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T154501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T153501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171231T141001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T194500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T182001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T181500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T181000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T164001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T163000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T150501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T150001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T145501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171230T145000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T191500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T190501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T173500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T172501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T160000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T155500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T155001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T154501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171229T142000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T183001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T182501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T182001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T165501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T165001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T164501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T164001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T151501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T151001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171228T150501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T192500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T192000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T191500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T174500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T174000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T173500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T161001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T160500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T160000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T143501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171227T143001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T184501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T184001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T183501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T183001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T170501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T170001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T165501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T153000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T152500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T152001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171226T151501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T193501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T193001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T192500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T180001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T175501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T162501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T162001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T161501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T161001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T144501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171225T144001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T185500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T185000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T184501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T172000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T171500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T171000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T170500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T154000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T153500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171224T153000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T194001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T181501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T181001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T180501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T180001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T163001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T162501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T145501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171223T145001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T190501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T190000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T185500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T172501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T172001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T155001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T154501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171222T141501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T182500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T182000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T181501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T164500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T164000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T151000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T150500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171221T150000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T192001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T191501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T174501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T174001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T173501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T160501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T160001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T155501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171220T142501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T183501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T183000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T182500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T170001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T165501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T165000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T152001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T151501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171219T151000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T193001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T192501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T192001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T175500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T174501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T161500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T161000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T160501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T144000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171218T143500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T185001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T184501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T184001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T171001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T170501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T170001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T153501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T153001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T152501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171217T152001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T194000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T193500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T180500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T180000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T175500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T163001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T162500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T162000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T161500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T145001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171216T144501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T190001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T185501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T185001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T172500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T172001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T171501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T171001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T154500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171215T153501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T194500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T182001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T181501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T181001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T180500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T164001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T163001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T150501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T150001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T145501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171214T145001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T191500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T191000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T190500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T190001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T173500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T173000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T172500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T160001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T155500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T155000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T154500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171213T142001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T183001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T182501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T182001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T165501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T165001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T164501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T164001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T151501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T151001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171212T150501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T192501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T192001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T191500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T174501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T174001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T173500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T161001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T160501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T160001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171211T143001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T184500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T184000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T183501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T183001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T170500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T170000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T165500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T153000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T152500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T152000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171210T151500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T193501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T193001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T192501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T180001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T175501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T162501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T162001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T161501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T161001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T144501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171209T144001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T185501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T185000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T184500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T172001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T171501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T171000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T170500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T153501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171208T153001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T194001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T181500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T181000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T180501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T180001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T163500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T163000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T162501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T145500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171207T145000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T190501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T190001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T185501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T172501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T172001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T155001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T154501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171206T141501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T182501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T182000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T181500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T164501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T164000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T163500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T151001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T150501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171205T150000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T192001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T191501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T174001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T173501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T160500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T160001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T155501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171204T142500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T183501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T183001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T182501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T170001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T165501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T165001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T152001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T151501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171203T151001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T193000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T192500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T192001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T175500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T175000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T174500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T161500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T161000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T160500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T144001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171202T143501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T185001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T184501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T184001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T171001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T170501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T170001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T153500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T153001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T152501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171201T152001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T194001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T193500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T180501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T180001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T175500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T163001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T162501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T162001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T161501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T145001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171130T144501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T190000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T185500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T185001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T172500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T172000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T171500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T171001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T154500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T154000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171129T153500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T194501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T182001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T181501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T181001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T180501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T164001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T163001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T150501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T150001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T145501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171128T145001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T191501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T190500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T190000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T173501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T172500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T160001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T155501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T155001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T154500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171127T142001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T183000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T182501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T182001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T165500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T165000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T164501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T164001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T151500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T151000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171126T150500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T192501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T192001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T191501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T174501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T174001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T173501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T161001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T160501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T160001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171125T143001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T184501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T184000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T183500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T183000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T170501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T170000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T165500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T153001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T152501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T152000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171124T151500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T193501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T193001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T192501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T180000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T175501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T162500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T162000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T161501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T161001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T144500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171123T144000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T185501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T185001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T184501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T172001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T171501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T171001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T170501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T153501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171122T153001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T194000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T181500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T181000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T180500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T180000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T163000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T162500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T145501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171121T145000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T190501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T190001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T185501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T172501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T172001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T155001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T154501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171120T141500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T182501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T182001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T181501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T164501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T164001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T151001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T150501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171119T150001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T192000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T191500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T174000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T173500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T160500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T160000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T155500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171118T142500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T183501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T183001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T182501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T170001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T165501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T165001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T152001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T151501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171117T151001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T193001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T192500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T192000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T175501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T175001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T174500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T161501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T161001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T160500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T144001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171116T143501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T185000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T184501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T184001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T171000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T170501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T170001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T153500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T153000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T152500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171115T152001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T194001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T193501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T180501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T180001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T175501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T163001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T162501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T162001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T161501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T145001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171114T144501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T190000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T185500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T185000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T172501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T172000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T171500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T171000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T154501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T154001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171113T153500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T194501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T182000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T181501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T181001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T180501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T164000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T163501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T163001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T150500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T150000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T145501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171112T145001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T191501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T191001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T190501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T190000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T173501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T173001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T172501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T160001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T155501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T155001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T154501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171111T142001.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T183000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T182500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T182000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T165501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T165000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T164500.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T164000.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T151501.L2.OC.nc",
    "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/AQUA_MODIS.20171110T151000.L2.OC.nc",
]

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
