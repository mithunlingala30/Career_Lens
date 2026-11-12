"""
MARKOV CHAIN  -  career-readiness stage transitions
===================================================
States S = {Beginner, Developing, Intermediate, Job-Ready, Advanced}.  Time step = 1 month of
focused skill development.  Transition matrix P (row-stochastic) for states 0..3:
    P[i, i+1] = a   (advance)     P[i, i-1] = r = 0.05 (lapse)     P[i, i] = 1 - a - r (stay)
with the advance probability driven by the candidate's data:
    a = clamp(0.15 + 0.45*readiness - 0.02*min(missing_skills, 8),  0.08, 0.70)
State 4 (Advanced) is absorbing. The row for state 0 puts the lapse mass on 'stay'.
Outputs
  * distribution after t months:           pi_t = pi_0 P^t
  * expected months to the next milestone: make the target absorbing, Q = transient block,
        fundamental matrix N = (I - Q)^-1,  expected steps = N 1
  * probability of reaching the milestone within t months (absorbing-chain power).
Assumptions: memoryless (Markov) progress, constant monthly rates, lapse rate fixed.
Limitation: transition probabilities are defined by the model above, not estimated from
longitudinal learner data.
"""
import numpy as np

STATES = ["Beginner", "Developing", "Intermediate", "Job-Ready", "Advanced"]
LAPSE = 0.05


def readiness_to_state(r: float) -> int:
    return 0 if r < 0.2 else 1 if r < 0.4 else 2 if r < 0.6 else 3 if r < 0.8 else 4


def transition_matrix(readiness: float, n_missing: int) -> np.ndarray:
    a = float(np.clip(0.15 + 0.45 * readiness - 0.02 * min(n_missing, 8), 0.08, 0.70))
    n = len(STATES)
    P = np.zeros((n, n))
    for i in range(n - 1):
        P[i, i + 1] = a
        if i > 0:
            P[i, i - 1] = LAPSE
        P[i, i] = 1 - P[i].sum()
    P[n - 1, n - 1] = 1.0
    return P


def analyze(readiness: float, n_missing: int, horizons=(1, 3, 6, 12)) -> dict:
    P = transition_matrix(readiness, n_missing)
    s = readiness_to_state(readiness)
    pi0 = np.zeros(len(STATES)); pi0[s] = 1
    dist = {int(t): [round(float(x), 4) for x in pi0 @ np.linalg.matrix_power(P, t)] for t in horizons}
    target = min(s + 1, 4) if s >= 3 else 3
    expected, reach = None, {}
    if s < 4:
        T = P[:target + 1, :target + 1].copy()
        T[target] = 0; T[target, target] = 1                 # make target absorbing
        T[:target] /= T[:target].sum(axis=1, keepdims=True)  # renormalise (no mass beyond target)
        Q = T[:target, :target]
        N = np.linalg.inv(np.eye(target) - Q)
        expected = float(N.sum(axis=1)[s]) if s < target else 0.0
        e = np.zeros(target + 1); e[s] = 1
        reach = {int(t): round(float((e @ np.linalg.matrix_power(T, t))[target]), 4) for t in horizons}
    return {"states": STATES, "current_state": s, "current_state_name": STATES[s],
            "target_state": target, "target_state_name": STATES[target],
            "advance_probability": round(float(P[0, 1]), 4),
            "transition_matrix": [{"from": STATES[i], "to": [round(float(v), 4) for v in row]} for i, row in enumerate(P)],   # list of maps (Firestore forbids nested arrays)
            "distribution": dist, "expected_months_to_target": None if expected is None else round(expected, 1),
            "probability_reach_target": reach}
