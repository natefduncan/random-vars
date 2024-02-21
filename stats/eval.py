from typing import Dict, Optional, Any
import numpy as np
import pandas as pd
from dataclasses import dataclass

from stats.parser import exprs_from_str, Distribution, Equation, Expression

Number = int | float

def get_random_mappings(rng: np.random.Generator) -> Dict[str, Any]:
    return {
        "norm": rng.normal,
        "binom": rng.binomial, 
        "poisson": rng.poisson, 
        "uniform": rng.uniform, 
        "unif": rng.uniform, 
        "integers": rng.integers, 
        "int": rng.integers, 
        "negbinom": rng.negative_binomial, 
        "gamma": rng.gamma, 
        "beta": rng.beta, 
        "exp": rng.exponential
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
        while True:
            for expression in self.expressions:
                if expression.variable in resolved:
                    continue

                if isinstance(expression, Distribution):
                    for a in expression.args:
                        if isinstance(a, Number) or isinstance(a, float):
                            pass
                        elif isinstance(a, str):
                            if a not in resolved:
                                continue

                        if all([isinstance(a, Number) for a in expression.args]):
                            output[expression.variable] = np.round(rand_mappings[expression.name](*[value for value in expression.args], size=nreps), decimals)
                        else:
                            clean_args = []
                            for a in expression.args:
                                if isinstance(a, str):
                                    clean_args.append(list(output[a]))
                                elif isinstance(a, Number):
                                    clean_args.append(np.round([a] * nreps, decimals))
                            output[expression.variable] = np.round([rand_mappings[expression.name](*args, size=1)[0] for args in zip(*clean_args)], decimals)
                    resolved.append(expression.variable)
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
