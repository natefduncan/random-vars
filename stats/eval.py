from typing import Dict, Optional, Any
import numpy as np
import pandas as pd
from dataclasses import dataclass

from stats.parser import exprs_from_str, Distribution, Equation, Expression

def get_random_mappings(rng: np.random.Generator) -> Dict[str, Any]:
    return {
        "norm": "rng.normal",
        "binom": "rng.binomial", 
        "poisson": "rng.poisson", 
        "uniform": "rng.uniform", 
        "unif": "rng.uniform", 
        "integers": "rng.integers", 
        "int": "rng.integers", 
        "negbinom": "rng.negative_binomial", 
        "gamma": "rng.gamma", 
        "beta": "rng.beta", 
        "exp": "rng.exponential", 
        "choice": "rng.choice", 
    }

@dataclass
class Eval:
    expressions: list[Expression]

    @classmethod
    def from_str(cls, input_str: str):
        return cls(exprs_from_str(input_str))

    def random(self, nreps: int, seed: Optional[int] = None, decimals: int = 2) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        rand_mappings = get_random_mappings(rng)
        output = {}
        resolved = []

        # Keep looping until all expression variables resolved
        while True:
            for expression in self.expressions:
                if expression.variable in resolved:
                    continue

                if isinstance(expression, Distribution):
                    try:
                        output[expression.variable] = np.round(eval(f"{rand_mappings[expression.name]}({expression.body}, size={nreps})", globals(), {**{"rng": rng}, **output}), decimals)
                        resolved.append(expression.variable)
                    except NameError as e:
                        print(e)
                        continue
                elif isinstance(expression, Equation):
                    try:
                        e = eval(expression.operations, globals(), output)
                    except Exception as e:
                        print(e)
                        continue
                    output[expression.variable] = e
                    resolved.append(expression.variable)

            if len(self.expressions) == len(resolved):
                break

        return pd.DataFrame(output)
