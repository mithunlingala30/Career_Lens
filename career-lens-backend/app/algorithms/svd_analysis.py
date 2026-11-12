"""
SINGULAR VALUE DECOMPOSITION  -  latent relationship between a candidate and job requirements
=============================================================================================
Let A (J x V) be the job-by-skill requirement matrix (entries importance/5).
    A = U S V^T      (U: job factors, S: singular values, V: skill factors)
Keeping the top k components gives the best rank-k approximation (Eckart-Young). Each right
singular vector v_f is a *latent skill family* (e.g. 'web stack', 'data science').
A candidate vector c (length V) is folded into the same latent space:   c_hat = c V_k
Jobs are projected the same way:                                       a_hat_j = a_j V_k
Latent fit = cosine(c_hat, a_hat_j), clipped to [0,1].  This credits a candidate who has skills
from the same *family* as the job even if the literal skills differ (e.g. Django vs Flask).
Assumption: skills co-occur in meaningful bundles in the job catalogue. Limitation: quality grows
with catalogue size; with few jobs only a handful of latent factors exist (k = min(3, rank)).
"""
import numpy as np


def latent_analysis(jobs: dict, candidate_skills: dict, k: int = 3) -> dict:
    """jobs: {job_id: {skill: importance}}; candidate_skills: {skill: strength}."""
    vocab = sorted({s for r in jobs.values() for s in r})
    ids = list(jobs)
    if not vocab or not ids:
        return {"similarities": {}, "explained_variance": [], "factors": [], "k": 0}
    A = np.array([[jobs[j].get(s, 0) / 5.0 for s in vocab] for j in ids])
    c = np.array([float(candidate_skills.get(s, 0.0)) for s in vocab])
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    k = int(max(1, min(k, len(S))))
    Vk = Vt[:k].T                      # V x k
    c_hat = c @ Vk                     # candidate in latent space
    A_hat = A @ Vk                     # jobs in latent space
    sims, job_latent = {}, {}
    for idx, jid in enumerate(ids):
        a = A_hat[idx]
        denom = np.linalg.norm(c_hat) * np.linalg.norm(a)
        sims[jid] = float(max(0.0, min(1.0, (c_hat @ a) / denom))) if denom > 1e-12 else 0.0
        job_latent[jid] = [round(float(x), 4) for x in a]
    energy = (S ** 2) / (S ** 2).sum()
    factors = []
    for f in range(k):
        load = Vt[f] * (1 if Vt[f][np.argmax(np.abs(Vt[f]))] > 0 else -1)   # fix sign for readability
        top = np.argsort(-np.abs(load))[:4]
        factors.append({"factor": f + 1, "singular_value": round(float(S[f]), 4),
                        "explained_variance": round(float(energy[f]), 4),
                        "top_skills": [vocab[i] for i in top],
                        "candidate_loading": round(float(c_hat[f]), 4)})
    return {"similarities": sims, "job_latent": job_latent, "candidate_latent": [round(float(x), 4) for x in c_hat],
            "explained_variance": [round(float(e), 4) for e in energy[:k]],
            "cumulative_variance": round(float(energy[:k].sum()), 4), "factors": factors, "k": k}
