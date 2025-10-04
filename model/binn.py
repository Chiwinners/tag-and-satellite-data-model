import math
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Optional
from config import BINN

def safe_logit(p: torch.Tensor, eps=1e-6):
    p = torch.clamp(p, eps, 1 - eps)
    return torch.log(p) - torch.log(1 - p)

class TabularDS(Dataset):
    def __init__(self, X, y, prior=None, weight=None):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).view(-1,1)
        self.prior = torch.tensor(prior, dtype=torch.float32).view(-1,1) if prior is not None else None
        self.weight = torch.tensor(weight, dtype=torch.float32).view(-1,1) if weight is not None else None
    def __len__(self): return len(self.X)
    def __getitem__(self, i):
        return self.X[i], self.y[i], (self.prior[i] if self.prior is not None else None), (self.weight[i] if self.weight is not None else None)

class BINNNet(nn.Module):
    def __init__(self, in_dim, hidden=[128,64], prior_mode="add_logit", prior_scale=1.0):
        super().__init__()
        layers = []
        last = in_dim
        for h in hidden:
            layers += [nn.Linear(last, h), nn.ReLU(), nn.Dropout(0.1)]
            last = h
        self.backbone = nn.Sequential(*layers) if layers else nn.Identity()
        self.head = nn.Linear(last if layers else in_dim, 1)
        self.prior_mode = prior_mode
        self.prior_scale = prior_scale

    def forward(self, x, prior=None):
        z = self.head(self.backbone(x))  # logit base
        if self.prior_mode == "add_logit" and prior is not None:
            # suma un sesgo informado por logit(prior)
            z = z + self.prior_scale * safe_logit(prior)
        elif self.prior_mode == "feature" and prior is not None:
            # concat prior como feature (simple)
            z = self.head(torch.cat([self.backbone(x), prior], dim=1))
        # else: no prior
        return z

def train_binn(Xtr, ytr, Xva, yva, prior_tr=None, prior_va=None, effort_tr=None, effort_va=None,
               in_dim=None, device="cpu"):
    torch.manual_seed(BINN["seed"])
    in_dim = in_dim or Xtr.shape[1]
    net = BINNNet(in_dim, BINN["hidden_sizes"], BINN["prior_mode"], BINN["prior_scale"]).to(device)

    ds_tr = TabularDS(Xtr, ytr, prior_tr, effort_tr if BINN["use_effort_as_weight"] else None)
    ds_va = TabularDS(Xva, yva, prior_va, effort_va if BINN["use_effort_as_weight"] else None)

    dl_tr = DataLoader(ds_tr, batch_size=BINN["batch_size"], shuffle=True, drop_last=False)
    dl_va = DataLoader(ds_va, batch_size=BINN["batch_size"], shuffle=False)

    opt = torch.optim.Adam(net.parameters(), lr=BINN["lr"], weight_decay=BINN["weight_decay"])
    bce = nn.BCEWithLogitsLoss(reduction="none")

    best = dict(auc=-1.0, state=None)

    def batch_auc(logits, y):
        with torch.no_grad():
            p = torch.sigmoid(logits).cpu().numpy().ravel()
            t = y.cpu().numpy().ravel()
            if len(np.unique(t))<2: return np.nan
            from sklearn.metrics import roc_auc_score
            return roc_auc_score(t, p)

    for epoch in range(BINN["epochs"]):
        net.train(); loss_sum=0.0
        for X, y, prior, w in dl_tr:
            X, y = X.to(device), y.to(device)
            prior = prior.to(device) if prior is not None else None
            w = w.to(device) if w is not None else None

            logits = net(X, prior)
            loss_vec = bce(logits, y)
            if w is not None:
                # normaliza pesos para estabilidad
                w = w / (w.mean() + 1e-8)
                loss_vec = loss_vec * w
            # regularización hacia el prior en probas (opcional)
            if prior is not None and BINN["lambda_prior_reg"] > 0.0:
                p = torch.sigmoid(logits)
                loss_prior = ((p - prior)**2).mean()
                loss = loss_vec.mean() + BINN["lambda_prior_reg"]*loss_prior
            else:
                loss = loss_vec.mean()

            opt.zero_grad()
            loss.backward()
            opt.step()
            loss_sum += loss.item()

        # valid
        net.eval()
        logits_va = []
        y_va_all = []
        with torch.no_grad():
            for X, y, prior, _ in dl_va:
                X, y = X.to(device), y.to(device)
                prior = prior.to(device) if prior is not None else None
                logits = net(X, prior)
                logits_va.append(logits.cpu())
                y_va_all.append(y.cpu())
        if len(logits_va):
            logits_va = torch.cat(logits_va, dim=0)
            y_va_all = torch.cat(y_va_all, dim=0)
            auc = batch_auc(logits_va, y_va_all)
        else:
            auc = np.nan

        if (auc is not np.nan) and (auc > best["auc"]):
            best["auc"] = auc
            best["state"] = {k:v.cpu() for k,v in net.state_dict().items()}

        print(f"[BINN] Epoch {epoch+1}/{BINN['epochs']} loss={loss_sum/len(dl_tr):.4f} valAUC={auc:.4f}")

    if best["state"] is not None:
        net.load_state_dict(best["state"])
    return net
