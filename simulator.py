"""Software-only stochastic RFID basket simulator; not RF physics."""
from dataclasses import dataclass
import random

@dataclass(frozen=True)
class Tag:
    epc: str
    price_paise: int
    inside: bool = True
    read_probability: float = 0.92

@dataclass(frozen=True)
class CheckoutResult:
    expected: frozenset[str]
    detected: frozenset[str]
    total_paise: int
    expected_total_paise: int
    @property
    def correct(self):
        return self.expected == self.detected
    @property
    def missing(self):
        return self.expected - self.detected
    @property
    def unexpected(self):
        return self.detected - self.expected

def scan(tags, *, cycles=4, seed=1, outside_leak_probability=0.03):
    if cycles < 1 or not 0 <= outside_leak_probability <= 1:
        raise ValueError("Invalid scanning parameters")
    tags = list(tags)
    if len({t.epc for t in tags}) != len(tags):
        raise ValueError("Physical products must have unique EPCs")
    if any(not 0 <= t.read_probability <= 1 or t.price_paise < 0 for t in tags):
        raise ValueError("Invalid tag parameters")
    rng = random.Random(seed)
    seen = set()
    for _ in range(cycles):
        for tag in tags:
            if rng.random() < (tag.read_probability if tag.inside else outside_leak_probability):
                seen.add(tag.epc)
    prices = {tag.epc: tag.price_paise for tag in tags}
    expected = frozenset(tag.epc for tag in tags if tag.inside)
    return CheckoutResult(expected, frozenset(seen),
                          sum(prices[e] for e in seen), sum(prices[e] for e in expected))

def trial_batch(*, inside_count=20, outside_count=1, trials=1000, cycles=4,
                read_probability=0.92, outside_leak_probability=0.03):
    tags = [Tag(f"IN-{i:03d}", 49900, True, read_probability) for i in range(inside_count)]
    tags += [Tag(f"OUT-{i:03d}", 99900, False) for i in range(outside_count)]
    outcomes = [scan(tags, cycles=cycles, seed=i,
                     outside_leak_probability=outside_leak_probability) for i in range(trials)]
    return {"trials": trials,
            "exact_basket_successes": sum(r.correct for r in outcomes),
            "missed_basket_trials": sum(bool(r.missing) for r in outcomes),
            "false_inclusion_trials": sum(bool(r.unexpected) for r in outcomes)}

if __name__ == "__main__":
    import json
    print(json.dumps(trial_batch(), indent=2))
