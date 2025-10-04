import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve, roc_curve

def optimal_threshold(y_true, y_prob, method="youden"):
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)
    if method == "youden":
        fpr, tpr, thr = roc_curve(y_true, y_prob)
        j = tpr - fpr
        i = np.argmax(j)
        return thr[i]
    elif method == "f1":
        p, r, thr = precision_recall_curve(y_true, y_prob)
        f1 = 2*p*r/(p+r+1e-8)
        i = np.nanargmax(f1[:-1])
        return thr[i]
    else:
        return 0.5
