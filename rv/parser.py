import enum
from dataclasses import dataclass
from typing import List, Optional, Union

from parsy import from_enum, regex, seq, string, alt

# AST Nodes

class Operator(enum.Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"

@dataclass
class Number:
    value: int

@dataclass
class Variable:
    value: str

Value = Union[Number, Variable]

@dataclass
class Distribution:
    variable: Variable
    name: str
    args: List[Value]

@dataclass
class Equation:
    variable: Variable
    left: Value
    operator: Operator
    right: Value

Statement = Union[Distribution, Equation]

Statements = List[Statement]

# Parsers
# x ~ norm(a, b); y ~ norm(c, d); z = x + y; 

number_literal = regex(r"-?[0-9]+").map(int).map(Number)

identifier = regex("[a-zA-Z][a-zA-Z0-9_]*")

variable = identifier.map(Variable)

value = number_literal | variable

space = regex(r"\s+")  # non-optional whitespace

padding = regex(r"\s*")  # optional whitespace

operator = from_enum(Operator)

equation = seq(
    variable=variable << padding,
    _equal = string("=") << padding, 
    left=value << padding,
    operator=operator << padding,
    right=value << padding
).combine_dict(Equation)

distribution = seq(
    variable=variable << padding, 
    _tilde = string("~") << padding,
    name = identifier << string("("),
    args=value.sep_by(padding + string(",") + padding, min=1) << string(")")
).combine_dict(Distribution)

statement = equation << string(";") | distribution << string(";")
statements = statement.sep_by(string(" "))

def test_distribution():
    assert statement.parse("x ~ norm(0, 1);") == Distribution(
        variable = Variable("x"), 
        name = "norm", 
        args = [Number(0), Number(1)]
    )

def test_equation():
    assert statement.parse("z = x + y;") == Equation(
        variable = Variable("z"), 
        left = Variable("x"), 
        operator = Operator.ADD, 
        right = Variable("y")
    )

def test_statements():
    assert statements.parse("x ~ norm(0, 1); z = x + y;") == [
            Distribution(
                variable = Variable("x"), 
                name = "norm", 
                args = [Number(0), Number(1)]
            ), 
            Equation(
                variable = Variable("z"), 
                left = Variable("x"), 
                operator = Operator.ADD, 
                right = Variable("y")
            )
        ]




