#!/usr/bin/env python
import random
from .base_agent import BaseAgent

class RandomAgent(BaseAgent):
    def __init__(self, rng_seed=20240815):
        self.rng = random.Random(rng_seed)

    def act(self, obs, info):
        # Choose a random action from the list provided in info.
        return self.rng.choice(info["actions"] + ["noop"])
