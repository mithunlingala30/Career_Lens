"""
CONDITIONAL PROBABILITY  -  P(Suitable | skill-coverage bin K, education met E, experience met X)
==============================================================================================
Estimated EMPIRICALLY from a labelled calibration set (see services/reference.py):

    P(S | K, E, X) = P(S and K and E and X) / P(K and E and X)  =  n(S,K,E,X) / n(K,E,X)

with Laplace (add-alpha) smoothing so empty cells never give 0 or 1:
    P_hat = (n_S + alpha) / (n + 2*alpha),   alpha = 1.
Coverage K is discretised: 0 (<0.4), 1 (0.4-0.7), 2 (>=0.7).
Assumption: the calibration cohort is representative. Limitation: it is simulated (documented in
README) so probabilities should be re-fitted once real hiring outcomes exist.
"""
ALPHA = 1.0


def coverage_bin(c: float) -> int:
    return 0 if c < 0.4 else (1 if c < 0.7 else 2)


def fit(cases: list) -> dict:
    """cases: dicts with coverage, edu_ok, exp_ok, label (bool). Returns a count table."""
    table = {}
    for c in cases:
        key = (coverage_bin(c["coverage"]), int(c["edu_ok"]), int(c["exp_ok"]))
        n_s, n = table.get(key, (0, 0))
        table[key] = (n_s + int(c["label"]), n + 1)
    return {"cells": table, "total": len(cases), "positives": sum(int(c["label"]) for c in cases)}


def estimate(table: dict, coverage: float, edu_ok: bool, exp_ok: bool) -> dict:
    kb = coverage_bin(coverage)
    key = (kb, int(edu_ok), int(exp_ok))
    n_s, n = table["cells"].get(key, (0, 0))
    total = max(table["total"], 1)
    p = (n_s + ALPHA) / (n + 2 * ALPHA)
    # marginal: condition on coverage bin only
    ms = sum(v[0] for k, v in table["cells"].items() if k[0] == kb)
    mn = sum(v[1] for k, v in table["cells"].items() if k[0] == kb)
    return {
        "p_conditional": float(p),
        "coverage_bin": ["low (<40%)", "medium (40-70%)", "high (>=70%)"][kb],
        "cell_support": int(n),
        "p_joint": float(n_s / total),
        "p_evidence": float(n / total),
        "p_given_coverage_only": float((ms + ALPHA) / (mn + 2 * ALPHA)),
        "base_rate": float((table["positives"] + ALPHA) / (total + 2 * ALPHA)),
    }
