"""
Deterministic Seeded Random Number Generator for reproducible analog horror rendering.
"""
import numpy as np


class DeterministicRNG:
    def __init__(self, seed: int = 19940514):
        self.master_seed = seed
        self.rng = np.random.RandomState(seed)

    def reseed(self, seed: int = None):
        if seed is None:
            seed = self.master_seed
        self.rng = np.random.RandomState(seed)

    def uniform(self, low: float = 0.0, high: float = 1.0, size=None):
        return self.rng.uniform(low, high, size=size)

    def normal(self, loc: float = 0.0, scale: float = 1.0, size=None):
        return self.rng.normal(loc, scale, size=size)

    def randint(self, low: int, high: int, size=None):
        return self.rng.randint(low, high, size=size)

    def choice(self, a, size=None, replace=True, p=None):
        return self.rng.choice(a, size=size, replace=replace, p=p)


# Global deterministic RNG instance
GLOBAL_RNG = DeterministicRNG(19940514)
