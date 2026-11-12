"""
INNER PRODUCT  -  candidate skill vector  .  job requirement vector
===================================================================
Both people and jobs are mapped into the same skill space  R^V  (V = union of skills).

    c_i = evidence strength of skill i on the resume  (1.0 = demonstrated in experience/projects,
          0.7 = listed only, 0 = absent)
    j_i = importance of skill i for the job / 5        (0 = not required, 1 = critical)

    <c, j>  = sum_i c_i * j_i                     (raw inner product)
    coverage = <c, j> / <1_J, j> = <c, j> / sum(j)  in [0,1]   -> share of weighted requirements met
    cosine   = <c, j> / (||c|| * ||j||)            -> directional similarity (penalises unrelated skills)

Assumption: skills contribute additively and independently. Limitation: no skill-to-skill
similarity (e.g. 'Flask' vs 'Django') - SVD (svd_analysis.py) covers that latent structure.
"""
import numpy as np


def inner_product_match(candidate_skills: dict, job_requirements: dict) -> dict:
    vocab = sorted(set(job_requirements) | set(candidate_skills))
    c = np.array([float(candidate_skills.get(s, 0.0)) for s in vocab])
    j = np.array([job_requirements.get(s, 0) / 5.0 for s in vocab])
    ip = float(c @ j)
    j_total = float(j.sum())
    nc, nj = float(np.linalg.norm(c)), float(np.linalg.norm(j))
    coverage = ip / j_total if j_total > 0 else 0.0
    cosine = ip / (nc * nj) if nc > 0 and nj > 0 else 0.0
    contributions = [
        {"skill": s, "candidate": float(ci), "job": float(ji), "product": float(ci * ji)}
        for s, ci, ji in zip(vocab, c, j) if ji > 0
    ]
    return {
        "inner_product": round(ip, 4),
        "max_inner_product": round(j_total, 4),
        "coverage": float(min(1.0, max(0.0, coverage))),
        "cosine": float(min(1.0, max(0.0, cosine))),
        "vocabulary_size": len(vocab),
        "contributions": contributions,
    }
