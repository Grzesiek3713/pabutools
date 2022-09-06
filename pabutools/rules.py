from model import Election

def _utilitarian_greedy_internal(e : Election, W):
    costW = sum(c.cost for c in W)
    remaining = set(c for c in e.profile if c not in W)
    ranked = sorted(remaining, key=lambda c : -sum(e.profile[c].values()))
    for c in ranked:
        if costW + c.cost <= e.budget:
            W.add(c)
            costW += c.cost
    return W

def utilitarian_greedy(e : Election):
    return _utilitarian_greedy_internal(e, set())

def _mes_internal(e : Election, real_budget=None):
    W = set()
    costW = 0
    remaining = set(c for c in e.profile)
    endow = {i : 1.0 * e.budget / len(e.voters) for i in e.voters}
    while True:
        next_candidate = None
        lowest_rho = float("inf")
        for c in remaining:
            if sum(endow[i] for i in e.profile[c]) >= c.cost:
                supporters_sorted = sorted(e.profile[c], key=lambda i: endow[i] / e.profile[c][i])
                price = c.cost
                util = sum(e.profile[c].values())
                for i in supporters_sorted:
                    if endow[i] * util >= price * e.profile[c][i]:
                        break
                    price -= endow[i]
                    util -= e.profile[c][i]
                rho = endow[supporters_sorted[-1]] / e.profile[c][supporters_sorted[-1]]
                if price > 0 and util > 0:
                    rho = price / util
                if rho < lowest_rho:
                    next_candidate = c
                    lowest_rho = rho
        if next_candidate is None:
            break
        else:
            W.add(next_candidate)
            costW += next_candidate.cost
            remaining.remove(next_candidate)
            for i in e.profile[next_candidate]:
                endow[i] -= min(endow[i], lowest_rho * e.profile[next_candidate][i])
            if real_budget is not None: #optimization for the binsearch variant
                if costW > real_budget:
                    return None
    return endow, W

def method_of_equal_shares(e : Election, completion='binsearch'):
    W = None
    if completion == 'binsearch':
        initial_budget = e.budget
        b_low = e.budget
        b_high = sum(c.cost for c in e.profile) * len(e.voters)
        while b_high - b_low >= 1:
            e.budget = (b_high + b_low) / 2.0
            res_med = _mes_internal(e, real_budget=initial_budget) #returns None if we exceed the original budget
            if res_med is None:
                b_high = e.budget
            else:
                b_low = e.budget
                _, W = res_med
        e.budget = initial_budget
    elif completion == None:
        _, W = _mes_internal(e)
    elif completion == 'utilitarian_greedy':
        _, W = _mes_internal(e)
        W = _utilitarian_greedy_internal(e, W)
    elif completion == 'phragmen':
        endow, W = _mes_internal(e)
        W = _phragmen_internal(e, endow, W)
    assert W is not None
    return W

def _phragmen_internal(e : Election, endow, W):
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

def phragmen(e : Election):
    endow = {i : 0.0 for i in e.voters}
    return _phragmen_internal(e, endow, set())
