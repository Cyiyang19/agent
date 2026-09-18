"""Teacher-written safe candidates; never execute model-generated code."""
def buggy_energy(power_w, hours):
    return power_w * hours

def fixed_energy(power_w, hours):
    if power_w < 0 or hours < 0:
        raise ValueError('power and hours must be non-negative')
    return power_w * hours / 1000

CANDIDATES = {'buggy': buggy_energy, 'fixed': fixed_energy}

def check_candidate(name):
    if name not in CANDIDATES:
        return ['unknown candidate']
    fn = CANDIDATES[name]
    errors = []
    for watts, hours, expected in [(1000, 2, 2), (500, 3, 1.5), (0, 2, 0)]:
        actual = fn(watts, hours)
        if actual != expected:
            errors.append(f'{watts} W x {hours} h: expected {expected} kWh, got {actual}')
    for watts, hours in [(-1, 1), (1, -1)]:
        try:
            fn(watts, hours)
            errors.append('negative input was not rejected')
        except ValueError:
            pass
    return errors
