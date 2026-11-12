"""
HYPOTHESIS TESTING  -  proposed matching algorithm vs. basic keyword matching
=============================================================================
Data: labelled validation cases (services/reference.py) - each has a ground-truth suitability
label y in {0,1} and a calibrated probability in [0,1] from each method (both calibrated the same way).
Test 1  Paired t-test on per-case squared error (Brier loss)  d_i = (b_i - y_i)^2 - (p_i - y_i)^2
        H0: mean(d) = 0     H1: mean(d) > 0  (proposed has lower error).   t = mean(d)/(sd(d)/sqrt(n))
Test 2  McNemar test on classification outcomes at threshold tau
        b = cases proposed right & baseline wrong,  c = reverse
        chi2 = (|b - c| - 1)^2 / (b + c)  ~  chi2(1) under H0 (equal error rates)
Effect size: Cohen's d_z = mean(d)/sd(d).  Significance level alpha = 0.05.
Assumptions: cases independent; differences approx. normal (n is large, CLT).
Limitation: validation cases are simulated, so the result demonstrates the method; it is not
evidence about real-world hiring outcomes.
"""
import numpy as np
from scipy import stats


def _metrics(y, pred_bin):
    y = np.asarray(y, bool); p = np.asarray(pred_bin, bool)
    tp = int((y & p).sum()); fp = int((~y & p).sum()); fn = int((y & ~p).sum()); tn = int((~y & ~p).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"accuracy": (tp + tn) / max(len(y), 1), "precision": prec, "recall": rec, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn}


def compare_methods(y_true, proposed, baseline, threshold: float = 0.5, alpha: float = 0.05) -> dict:
    y = np.asarray(y_true, float); p = np.asarray(proposed, float); b = np.asarray(baseline, float)
    se_p, se_b = (p - y) ** 2, (b - y) ** 2
    d = se_b - se_p
    t, pv = stats.ttest_rel(se_b, se_p, alternative="greater")
    sd = d.std(ddof=1)
    dz = float(d.mean() / sd) if sd > 0 else 0.0
    cp_, cb_ = (p >= threshold) == (y == 1), (b >= threshold) == (y == 1)
    b01, c01 = int((cp_ & ~cb_).sum()), int((~cp_ & cb_).sum())
    chi2 = ((abs(b01 - c01) - 1) ** 2) / (b01 + c01) if b01 + c01 else 0.0
    mp = float(stats.chi2.sf(chi2, 1)) if b01 + c01 else 1.0
    sig_t, sig_m = bool(pv < alpha), bool(mp < alpha)
    concl = ("Reject H0: the proposed algorithm has significantly lower prediction error than keyword matching."
             if sig_t else "Fail to reject H0: no significant improvement over keyword matching was detected.")
    return {
        "n": int(len(y)), "alpha": alpha, "threshold": threshold,
        "proposed": {**_metrics(y, p >= threshold), "brier": float(se_p.mean())},
        "baseline": {**_metrics(y, b >= threshold), "brier": float(se_b.mean())},
        "paired_t_test": {"t": float(t), "p_value": float(pv), "mean_difference": float(d.mean()),
                          "cohens_dz": dz, "significant": sig_t, "hypothesis": "H0: mean error difference = 0 vs H1: proposed error < baseline error"},
        "mcnemar_test": {"proposed_only_correct": b01, "baseline_only_correct": c01, "chi2": float(chi2),
                         "p_value": mp, "significant": sig_m},
        "conclusion": concl,
    }
