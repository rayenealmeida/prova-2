"""
Implementa o transformador da árvore sintática que converte entre as representações

    lark.Tree -> lox.ast.Node.

A resolução de vários exercícios requer a modificação ou implementação de vários
métodos desta classe.
"""

from typing import Callable, Optional

from lark import Transformer, v_args

from . import runtime as op
from .ast import *


def op_handler(op: Callable):
    """
    Fábrica de métodos que lidam com operações binárias na árvore sintática.

    Recebe a função que implementa a operação em tempo de execução.
    """
    def method(self, left, right):
        return BinOp(left, right, op)
    return method


@v_args(inline=True)
class LoxTransformer(Transformer):
    # Programa
    def program(self, *stmts):
        return Program(list(stmts))

    # Operações matemáticas básicas
    mul = op_handler(op.mul)
    div = op_handler(op.truediv)
    sub = op_handler(op.sub)
    add = op_handler(op.add)

    # Comparações
    gt = op_handler(op.gt)
    lt = op_handler(op.lt)
    ge = op_handler(op.ge)
    le = op_handler(op.le)
    eq = op_handler(op.eq)
    ne = op_handler(op.ne)

    # Outras expressões
    def call(self, name: Var, params: list):
        return Call(name.name, params)

    def params(self, *args):
        params = list(args)
        return params

    # Comandos
    def print_cmd(self, expr):
        return Print(expr)

    def return_stmt(self, expr=None):
        return Return(expr)

    def if_cmd(self, condition, then_branch, else_branch=None):
        return If(condition, then_branch, else_branch)

    def while_cmd(self, condition, body):
        return While(condition, body)

    def do_while_cmd(self, body, condition):
        return DoWhile(condition, body)

    def for_cmd(self, initializer=None, condition=None, increment=None, body=None):
        return For(initializer, condition, increment, body)

    def assign_expr(self, name, value):
        return Assign(name, value)

    def type_hint(self, type_name):
        if isinstance(type_name, Type):
            return type_name
        return Type(str(type_name))

    def type_nullable(self, type_name):
        return Type(str(type_name), nullable=True)

    def var_def(self, name, type_hint=None, initializer=None):
        name_str = name.name if isinstance(name, Var) else str(name)
        return VarDef(name_str, initializer, type_hint)


    def fun_def(self, name, params, return_type=None, body=None):
        name_str = str(name)
        return Function(name_str, params, return_type, body)


    def lambda_expr(self, params, return_type=None, body=None):
        return Lambda(params, body, return_type)

    def params_def(self, *args):
        return list(args)

    def param_def(self, name, type_hint=None):
        name_str = str(name)
        return (name_str, type_hint)

    # Blocks
    def block(self, *stmts):
        return Block(list(stmts))

    def block_expr(self, *items):
        *stmts, expr = items
        return BlockExpr(list(stmts), expr)

    # Tokens
    def VAR(self, token):
        name = str(token)
        return Var(name)

    def NUMBER(self, token):
        num = float(token)
        return Literal(num)

    def STRING(self, token):
        text = str(token)[1:-1]
        return Literal(text)

    def NIL(self, _):
        return Literal(None)

    def BOOL(self, token):
        return Literal(token == "true")
    