"""
BAYES' THEOREM  -  P(Suitable | evidence)
=========================================
    P(S | E) = P(E | S) P(S) / [ P(E | S) P(S) + P(E | ~S) P(~S) ]

Evidence E is the set of required skills (each present / absent) plus education and experience
fit. Under a naive-Bayes (conditional independence) assumption the posterior is computed in
log-odds form:

    log O(S | E) = log O(S) + sum_k  w_k * log [ P(e_k | S) / P(e_k | ~S) ]

Per-skill likelihoods (ASSUMPTIONS - expert-set, not fitted):
    P(skill present | suitable)     = 0.85       P(skill present | not suitable) = 0.25
    P(skill absent  | suitable)     = 0.15       P(skill absent  | not suitable) = 0.75
Soft evidence: a skill with strength s in [0,1] contributes  s*LLR_present + (1-s)*LLR_absent.
Importance weights w_k = importance_k / mean importance, so critical skills move the posterior more.
Because naive-Bayes over-counts correlated skills, the skill evidence is tempered by using at most
6 'effective' skills:  n_eff = min(n, 6)  times the AVERAGE weighted log-likelihood ratio.
Education / experience enter as likelihood ratios (met 1.5 / 1.6, unmet 0.6 / 0.5).
Prior P(S) = 0.35 (assumed base rate of a random applicant being suitable).
Limitation: the numbers above are assumptions; conditional_probability.py provides an
empirical (data-driven) counterpart and the two are averaged in scoring.py.
"""
import math

P_PRESENT_S, P_PRESENT_NS = 0.85, 0.25
PRIOR = 0.35
LLR_PRESENT = math.log(P_PRESENT_S / P_PRESENT_NS)
LLR_ABSENT = math.log((1 - P_PRESENT_S) / (1 - P_PRESENT_NS))


def _logit(p): return math.log(p / (1 - p))
def _sigmoid(x): return 1.0 / (1.0 + math.exp(-max(-30, min(30, x))))


def posterior_suitability(skill_evidence, edu_ok: bool, exp_ratio: float, prior: float = PRIOR) -> dict:
    """skill_evidence: list of (importance 1..5, strength 0..1) for every required skill."""
    n = len(skill_evidence)
    edu_lr = 1.5 if edu_ok else 0.6
    exp_lr = 1.6 if exp_ratio >= 1 else (1.0 if exp_ratio >= 0.5 else 0.5)
    skill_llr = 0.0
    if n:
        mean_imp = sum(i for i, _ in skill_evidence) / n
        avg = sum((imp / mean_imp) * (s * LLR_PRESENT + (1 - s) * LLR_ABSENT) for imp, s in skill_evidence) / n
        skill_llr = min(n, 6) * avg
    log_odds = _logit(prior) + skill_llr + math.log(edu_lr) + math.log(exp_lr)
    post = _sigmoid(log_odds)
    return {
        "prior": prior,
        "posterior": float(post),
        "skill_log_likelihood_ratio": float(skill_llr),
        "education_likelihood_ratio": edu_lr,
        "experience_likelihood_ratio": exp_lr,
        "bayes_factor": float(math.exp(max(-30, min(30, log_odds - _logit(prior))))),
    }
