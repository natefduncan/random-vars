from typing import List, Dict
import numpy as np
import pandas as pd
from dataclasses import dataclass

from rv.parser import statements, Statement, Distribution, Equation, Number, Variable, Value, Operator

RANDOM_MAPPINGS = {
    "norm": np.random.normal,
    "binom": np.random.binomial, 
    "poisson": np.random.poisson, 
    "uniform": np.random.uniform, 
    "negbinom": np.random.negative_binomial, 
    "gamma": np.random.gamma, 
    "beta": np.random.beta, 
    "exp": np.random.exponential
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

    def random(self, nreps: int) -> pd.DataFrame:
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
                            output[statement.variable.value] = RANDOM_MAPPINGS[statement.name](*[value.value for value in statement.args], size=nreps)
                        else:
                            clean_args = []
                            for a in statement.args:
                                if isinstance(a, Variable):
                                    clean_args.append(list(output[a.value]))
                                elif isinstance(a, Number):
                                    clean_args.append([a.value] * nreps)
                            output[statement.variable.value] = [RANDOM_MAPPINGS[statement.name](*args, size=1)[0] for args in zip(*clean_args)]
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
