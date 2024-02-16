from dataclasses import dataclass

def isfloat(x):
    try:
        a = float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except (TypeError, ValueError):
        return False
    else:
        return a == b

@dataclass
class Distribution:
    variable: str
    name: str
    args: list[str | int | float]

@dataclass
class Equation:
    variable: str
    operations: str

Expression = Distribution | Equation

def exprs_from_str(s: str) -> list[Expression]:
    return [expr_from_str(i.replace("\n", "")) for i in s.split(";") if i]

def expr_from_str(s: str) -> Expression:
    s = s.replace(";", "")
    if "=" in s:
        # Equation
        variable, operations = s.split("=")
        return Equation(variable.strip(), operations.strip())
    elif "~" in s:
        # Distribution
        variable, dist = s.split("~")
        name, args_s = dist.split("(")
        args_s = args_s.replace(")", "")
        args_ls = [i.strip() for i in args_s.split(",")]
        args = []
        for a in args_ls:
            if isint(a):
                args.append(int(a))
            elif isfloat(a):
                args.append(float(a))
            else: 
                args.append(a)
        return Distribution(variable.strip(), name.strip(), args)
    else:
        raise ValueError(f"String {s} is not an equation or distribution")

def test_distribution():
    assert expr_from_str("x ~ norm(0, 1);") == Distribution(
        variable = "x", 
        name = "norm", 
        args = [0, 1]
    )

def test_float():
    assert expr_from_str("x ~ norm(0.5, 0.25);") == Distribution(
            variable = "x", 
            name = "norm", 
            args = [0.5, 0.25]
            )

def test_equation():
    assert expr_from_str("z = x + y;") == Equation(
        variable = "z", 
        operations= "x + y"
    )

def test_statements():
    assert exprs_from_str("x ~ norm(0, 1); z = x + y;") == [
            Distribution(
                variable = "x", 
                name = "norm", 
                args = [0, 1]
            ), 
            Equation(
                variable = "z", 
                operations = "x + y"
            )
        ]




