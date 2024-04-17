from dataclasses import dataclass
import re

@dataclass
class Distribution:
    variable: str
    name: str
    body: str

@dataclass
class Equation:
    variable: str
    operations: str

Expression = Distribution | Equation

def exprs_from_str(s: str) -> list[Expression]:
    return [expr_from_str(i.strip()) for i in s.split(";") if i.strip()]

def expr_from_str(s: str) -> Expression:
    # Delete comments
    comment_re = r"^#.+$"
    s = re.sub(comment_re, '', s, flags=re.M).strip()
    s = s.replace("\n", "")
    if "~" in s:
        # Distribution
        variable, dist = s.split("~")
        name, args_s = dist.split("(")
        args_s = args_s.replace(")", "")
        return Distribution(variable.strip(), name.strip(), args_s)
    else:
        # Equation
        variable, operations = s.split("=")
        return Equation(variable.strip(), operations.strip())

def test_distribution():
    assert expr_from_str("x ~ norm(0, 1);") == Distribution(
        variable = "x", 
        name = "norm", 
        body = "0, 1"
    )

def test_float():
    assert expr_from_str("x ~ norm(0.5, 0.25);") == Distribution(
            variable = "x", 
            name = "norm", 
            body = "0.5, 0.25", 
            )

def test_equation():
    assert expr_from_str("z = x + y;") == Equation(
        variable = "z", 
        operations= "x + y"
    )

def test_array():
    assert expr_from_str("x ~ choice([0, 1]);") == Distribution(
        variable="x", 
        name="choice", 
        body="[0, 1]",
    )

def test_kwargs():
    assert expr_from_str("z = x + y;") == Equation(
        variable = "z", 
        operations= "x + y"
    )

def test_statements():
    assert exprs_from_str("x ~ norm(0, 1); z = x + y;") == [
            Distribution(
                variable = "x", 
                name = "norm", 
                body = "0, 1", 
            ), 
            Equation(
                variable = "z", 
                operations = "x + y"
            )
        ]




