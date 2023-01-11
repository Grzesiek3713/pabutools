from .model import Election, Candidate, Voter
import math


###############################################################################
######################## UTILITARIAN GREEDY ###################################
###############################################################################


def _utilitarian_greedy_internal(e : Election, W : set[Candidate]) -> set[Candidate]:
    costW = sum(c.cost for c in W)
    remaining = set(c for c in e.profile if c not in W)
    ranked = sorted(remaining, key=lambda c : -sum(e.profile[c].values()))
    for c in ranked:
        if costW + c.cost <= e.budget:
            W.add(c)
            costW += c.cost
    return W

def utilitarian_greedy(e : Election) -> set[Candidate]:
    return _utilitarian_greedy_internal(e, set())


###############################################################################
################# PHRAGMEN'S SEQUENTIAL RULE ##################################
###############################################################################


def _phragmen_internal(e : Election, endow : dict[Voter, float], W : set[Candidate]) -> set[Candidate]:
    payment = {i : {} for i in e.voters}
    remaining = set(c for c in e.profile if c not in W)
    costW = sum(c.cost for c in W)
    while True:
        next_candidate = None
        lowest_time = float("inf")
        for c in remaining:
            if costW + c.cost <= e.budget:
                time = float(c.cost - sum(endow[i] for i in e.profile[c])) / len(e.profile[c])
                if time < lowest_time:
                    next_candidate = c
                    lowest_time = time
        if next_candidate is None:
            break
        W.add(next_candidate)
        costW += next_candidate.cost
        remaining.remove(next_candidate)
        for i in e.voters:
            if i in e.profile[next_candidate]:
                payment[i][next_candidate] = endow[i]
                endow[i] = 0
            else:
                endow[i] += lowest_time
    return W

def phragmen(e : Election) -> set[Candidate]:
    endow = {i : 0.0 for i in e.voters}
    return _phragmen_internal(e, endow, set())


###############################################################################
####################### METHOD OF EQUAL SHARES ################################
###############################################################################


def _mes_internal(e : Election, real_budget : int = 0) -> (dict[Voter, float], set[Candidate]):
    W = set()
    costW = 0
    remaining = set(c for c in e.profile)
    endow = {i : 1.0 * e.budget / len(e.voters) for i in e.voters}
    rho = {c : c.cost / sum(e.profile[c].values()) for c in e.profile}
    while True:
        next_candidate = None
        lowest_rho = float("inf")
        remaining_sorted = sorted(remaining, key=lambda c: rho[c])
        for c in remaining_sorted:
            if rho[c] >= lowest_rho:
                break
            if sum(endow[i] for i in e.profile[c]) >= c.cost:
                supporters_sorted = sorted(e.profile[c], key=lambda i: endow[i] / e.profile[c][i])
                price = c.cost
                util = sum(e.profile[c].values())
                for i in supporters_sorted:
                    if endow[i] * util >= price * e.profile[c][i]:
                        break
                    price -= endow[i]
                    util -= e.profile[c][i]
                rho[c] = price / util
                if rho[c] < lowest_rho:
                    next_candidate = c
                    lowest_rho = rho[c]
        if next_candidate is None:
            break
        else:
            W.add(next_candidate)
            costW += next_candidate.cost
            remaining.remove(next_candidate)
            for i in e.profile[next_candidate]:
                endow[i] -= min(endow[i], lowest_rho * e.profile[next_candidate][i])
            if real_budget: #optimization for 'increase-budget' completions
                if costW > real_budget:
                    return None
    return endow, W

def _is_exhaustive(e : Election, W : set[Candidate]) -> bool:
    costW = sum(c.cost for c in W)
    minRemainingCost = min([c.cost for c in e.profile if c not in W], default=math.inf)
    return costW + minRemainingCost > e.budget

def equal_shares(e : Election, completion : str = None) -> set[Candidate]:
    endow, W = _mes_internal(e)
    if completion is None:
        return W
    if completion == 'binsearch':
        initial_budget = e.budget
        while not _is_exhaustive(e, W): #we keep multiplying budget by 2 to find lower and upper bounds for budget
            b_low = e.budget
            e.budget *= 2
            res_nxt = _mes_internal(e, real_budget=initial_budget)
            if res_nxt is None:
                break
            _, W = res_nxt
        b_high = e.budget
        while not _is_exhaustive(e, W) and b_high - b_low >= 1: #now we perform the classical binary search
            e.budget = (b_high + b_low) / 2.0
            res_med = _mes_internal(e, real_budget=initial_budget)
            if res_med is None:
                b_high = e.budget
            else:
                b_low = e.budget
                _, W = res_med
        e.budget = initial_budget
        return W
    if completion == 'utilitarian_greedy':
        return _utilitarian_greedy_internal(e, W)
    if completion == 'phragmen':
        return _phragmen_internal(e, endow, W)
    if completion == 'add1':
        initial_budget = e.budget
        while not _is_exhaustive(e, W):
            e.budget += len(e.voters)
            res_nxt = _mes_internal(e, real_budget=initial_budget)
            if res_nxt is None:
                break
            _, W = res_nxt
        e.budget = initial_budget
        return W
    assert False, f"""Invalid value of parameter completion. Expected one of the following:
        * 'binsearch',
        * 'utilitarian_greedy',
        * 'phragmen',
        * 'add1',
        * None."""
