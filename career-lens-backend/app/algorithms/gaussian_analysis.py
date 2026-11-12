"""
GAUSSIAN (NORMAL) DISTRIBUTION  -  where does this resume score sit within the cohort?
====================================================================================
Model the reference scores X ~ N(mu, sigma^2) with sample estimates
    mu_hat = mean(X),   sigma_hat = std(X, ddof=1)
    z = (x - mu_hat) / sigma_hat        percentile = Phi(z) * 100
    pdf f(x) = 1/(sigma sqrt(2 pi)) exp(-(x-mu)^2 / (2 sigma^2))
The normality assumption is *checked* with a Shapiro-Wilk test and reported (p < 0.05 means the
Gaussian is only an approximation; the empirical percentile is returned alongside).
The 95% CI for the mean uses  mu +- 1.96 sigma / sqrt(n).
"""
import numpy as np
from scipy import stats


def analyze(score: float, reference_scores, source: str = "") -> dict:
    x = np.asarray(reference_scores, dtype=float)
    mu = float(x.mean())
    sigma = float(max(x.std(ddof=1), 1e-6)) if len(x) > 1 else 1.0
    z = (score - mu) / sigma
    pct = float(stats.norm.cdf(z) * 100)
    emp = float(((x < score).mean() + 0.5 * (x == score).mean()) * 100)
    sw_p = None
    if 3 <= len(x) <= 5000 and np.ptp(x) > 0:
        sw_p = float(stats.shapiro(x).pvalue)
    band = ("Exceptional (top 10%)" if pct >= 90 else "Strong (top 25%)" if pct >= 75 else
            "Above average" if pct >= 55 else "Average" if pct >= 40 else
            "Below average" if pct >= 20 else "Needs significant improvement")
    xs = np.linspace(0, 100, 51)
    curve = [{"x": float(a), "density": float(b)} for a, b in zip(xs, stats.norm.pdf(xs, mu, sigma))]
    half = 1.96 * sigma / np.sqrt(len(x)) if len(x) > 1 else 0
    return {"score": float(score), "mean": mu, "std": sigma, "n": int(len(x)), "z_score": float(z),
            "percentile": pct, "empirical_percentile": emp, "band": band, "source": source,
            "mean_ci95": [float(mu - half), float(mu + half)], "shapiro_p": sw_p,
            "normality_ok": (sw_p is None or sw_p >= 0.05), "curve": curve}
