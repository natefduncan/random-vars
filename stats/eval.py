from typing import List, Dict, Optional, Any
import numpy as np
import pandas as pd
from dataclasses import dataclass

from stats.parser import statements, Statement, Distribution, Equation, Number, Variable, Value, Operator

def get_random_mappings(rng: np.random.Generator) -> Dict[str, Any]:
    return {
        "norm": rng.normal,
        "binom": rng.binomial, 
        "poisson": rng.poisson, 
        "uniform": rng.uniform, 
        "unif": rng.uniform, 
        "negbinom": rng.negative_binomial, 
        "gamma": rng.gamma, 
        "beta": rng.beta, 
        "exp": rng.exponential
    }

def to_int(value: Value, output: Dict[str, np.ndarray], i: int) -> int:
    if isinstance(value, Number):
        return value.value
    elif isinstance(value, Variable):
        return output[value.value][i]

@dataclass
class Eval:
    statements: list[Statement]

    @classmethod
    def from_str(cls, input_str: str):
        return cls(statements.parse(input_str))

    def random(self, nreps: int, seed: Optional[int] = None) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        rand_mappings = get_random_mappings(rng)
        output = {}
        resolved = []
        while True:
            for statement in self.statements:
                if statement.variable.value in resolved:
                    continue

                if isinstance(statement, Distribution):
                    for a in statement.args:
                        if isinstance(a, Number):
                            pass
                        elif isinstance(a, Variable):
                            if a.value not in resolved:
                                continue

                        if all([isinstance(a, Number) for a in statement.args]):
                            output[statement.variable.value] = rand_mappings[statement.name](*[value.value for value in statement.args], size=nreps)
                        else:
                            clean_args = []
                            for a in statement.args:
                                if isinstance(a, Variable):
                                    clean_args.append(list(output[a.value]))
                                elif isinstance(a, Number):
                                    clean_args.append([a.value] * nreps)
                            output[statement.variable.value] = [rand_mappings[statement.name](*args, size=1)[0] for args in zip(*clean_args)]
                    resolved.append(statement.variable.value)
                elif isinstance(statement, Equation):
                    l = statement.left.value
                    r = statement.right.value
                    if l not in resolved or r not in resolved:
                        continue

                    op = statement.operator
                    if op == Operator.ADD:
                        output[statement.variable.value] = output[l] + output[r]
                    elif op == Operator.SUBTRACT:
                        output[statement.variable.value] = output[l] - output[r]
                    elif op == Operator.MULTIPLY:
                        output[statement.variable.value] = output[l] * output[r]
                    elif op == Operator.DIVIDE:
                        output[statement.variable.value] = output[l] / output[r]
                    resolved.append(statement.variable.value)

            if len(self.statements) == len(resolved):
                break

        return pd.DataFrame(output)
