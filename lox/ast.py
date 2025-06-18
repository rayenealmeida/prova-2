from abc import ABC
from dataclasses import dataclass, field
from typing import Callable, Optional

from .ctx import Ctx
from .node import Node

#
# TIPOS BÁSICOS
#

# Tipos de valores que podem aparecer durante a execução do programa
Value = bool | str | float | None


@dataclass
class Type(Node):
    """
    Representa uma declaração de tipo.
    """
    name: str
    nullable: bool = False


class Expr(Node, ABC):
    """
    Classe base para expressões.

    Expressões são nós que podem ser avaliados para produzir um valor.
    Também podem ser atribuídos a variáveis, passados como argumentos para
    funções, etc.
    """


class Stmt(Node, ABC):
    """
    Classe base para comandos.

    Comandos são associdos a construtos sintáticos que alteram o fluxo de
    execução do código ou declaram elementos como classes, funções, etc.
    """


@dataclass
class Program(Node):
    """
    Representa um programa.

    Um programa é uma lista de comandos.
    """

    stmts: list[Stmt]

    def eval(self, ctx: Ctx):
        for stmt in self.stmts:
            stmt.eval(ctx)


#
# EXPRESSÕES
#

@dataclass

class BinOp(Expr):
    left: Expr
    right: Expr
    op: Callable[[Value, Value], Value]

    def eval(self, ctx: Ctx):
        left_value = self.left.eval(ctx)
        right_value = self.right.eval(ctx)
        
        if (isinstance(self.left, Var) and is_integer_var(self.left.name) and
            isinstance(self.right, Var) and is_integer_var(self.right.name)):
            left_value = to_integer(left_value)
            right_value = to_integer(right_value)
            result = self.op(left_value, right_value)
            return int(result)
        
        return self.op(left_value, right_value)


@dataclass
class Var(Expr):
    """
    Uma variável no código

    Ex.: x, y, z
    """

    name: str

    def eval(self, ctx: Ctx):
        try:
            return ctx[self.name]
        except KeyError:
            raise NameError(f"variável {self.name} não existe!")


@dataclass
class Literal(Expr):
    """
    Representa valores literais no código, ex.: strings, booleanos,
    números, etc.

    Ex.: "Hello, world!", 42, 3.14, true, nil
    """

    value: Value

    def eval(self, ctx: Ctx):
        return self.value


@dataclass
class And(Expr):
    """
    Uma operação infixa com dois operandos.

    Ex.: x and y
    """


@dataclass
class Or(Expr):
    """
    Uma operação infixa com dois operandos.
    Ex.: x or y
    """


@dataclass
class UnaryOp(Expr):
    """
    Uma operação prefixa com um operando.

    Ex.: -x, !x
    """


@dataclass
class Call(Expr):
    """
    Uma chamada de função.

    Ex.: fat(42)
    """

    name: str
    params: list[Expr]

    def eval(self, ctx: Ctx):
        func = ctx[self.name]
        params = []
        for param in self.params:
            params.append(param.eval(ctx))

        if callable(func):
            return func(*params)
        raise TypeError(f"{self.name} não é uma função!")


@dataclass
class This(Expr):
    """
    Acesso ao `this`.

    Ex.: this
    """


@dataclass
class Super(Expr):
    """
    Acesso a method ou atributo da superclasse.

    Ex.: super.x
    """


@dataclass
class Assign(Expr):
    """
    Atribuição de variável.

    Ex.: x = 42
    """
    name: str
    value: Expr

    def eval(self, ctx: Ctx):
        value = self.value.eval(ctx)
        if self.name and self.name[0].lower() in {'i', 'j', 'k', 'l', 'm', 'n'}:
            if isinstance(value, str):
                try:
                    value = int(float(value))
                except (ValueError, TypeError):
                    value = 0
            elif isinstance(value, (float, int)):
                value = int(value)
        ctx[self.name] = value
        return value


@dataclass
class Getattr(Expr):
    """
    Acesso a atributo de um objeto.

    Ex.: x.y
    """


@dataclass
class Setattr(Expr):
    """
    Atribuição de atributo de um objeto.

    Ex.: x.y = 42
    """
    obj: Expr
    attr: str
    value: Expr

    def eval(self, ctx: Ctx):
        obj = self.obj.eval(ctx)
        value = self.value.eval(ctx)
        # Aplica conversão para inteiro se o nome do atributo começar com i, j, k, l, m ou n
        if self.attr and self.attr[0].lower() in {'i', 'j', 'k', 'l', 'm', 'n'}:
            if isinstance(value, str):
                try:
                    value = int(float(value))
                except (ValueError, TypeError):
                    value = 0
            elif isinstance(value, (float, int)):
                value = int(value)
        setattr(obj, self.attr, value)
        return value

#
# COMANDOS
#
@dataclass
class Print(Stmt):
    """
    Representa uma instrução de impressão.

    Ex.: print "Hello, world!";
    """

    expr: Expr

    def eval(self, ctx: Ctx):
        value = self.expr.eval(ctx)
        print(value)


@dataclass
class Return(Stmt):
    """
    Representa uma instrução de retorno.

    Ex.: return x;
    """
    expr: Optional[Expr] = None


@dataclass
class VarDef(Stmt):
    """
    Representa uma declaração de variável.

    Ex.: var x = 42;
    """
    name: str
    initializer: Optional[Expr] = None
    type_hint: Optional[Type] = None

    def eval(self, ctx: Ctx):
        if self.initializer is not None:
            value = self.initializer.eval(ctx)
            # Aplica conversão para inteiro se o nome da variável começar com i, j, k, l, m ou n
            if self.name and self.name[0].lower() in {'i', 'j', 'k', 'l', 'm', 'n'}:
                if isinstance(value, str):
                    try:
                        value = int(float(value))
                    except (ValueError, TypeError):
                        value = 0
                elif isinstance(value, (float, int)):
                    value = int(value)
            ctx[self.name] = value



@dataclass
class If(Stmt):
    """
    Representa uma instrução condicional.

    Ex.: if (x > 0) { ... } else { ... }
    """
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt] = None


@dataclass
class For(Stmt):
    """
    Representa um laço de repetição.

    Ex.: for (var i = 0; i < 10; i++) { ... }
    """
    initializer: Optional[Stmt]
    condition: Optional[Expr]
    increment: Optional[Expr]
    body: Stmt


@dataclass
class While(Stmt):
    """
    Representa um laço de repetição.

    Ex.: while (x > 0) { ... }
    """
    condition: Expr
    body: Stmt


@dataclass
class Block(Node):
    """
    Representa bloco de comandos.

    Ex.: { var x = 42; print x;  }
    """
    stmts: list[Stmt]


@dataclass
class Function(Stmt):
    name: str
    params: list[tuple[str, Optional[Type]]] = field(default_factory=list)
    return_type: Optional[Type] = None
    body: Optional[Block] = None

    def eval(self, ctx: Ctx):
        def lox_function(*args):
            env = {}
            for (param_name, _), arg in zip(self.params, args):
                env[param_name] = arg
            env = ctx.push(env)
            try:
                if self.body:
                    for stmt in self.body.stmts:
                        stmt.eval(env)
            except Return as e:
                return e.value
            return None

        ctx[self.name] = lox_function

@dataclass
class Class(Stmt):
    """
    Representa uma classe.

    Ex.: class B < A { ... }
    """
    name: str
    superclass: Optional[Var] = None
    methods: list[Function] = field(default_factory=list)

@dataclass
class VarDef(Stmt):
    name: str
    initializer: Optional[Expr] = None
    type_hint: Optional[Type] = None

    def eval(self, ctx: Ctx):
        if self.initializer is not None:
            value = self.initializer.eval(ctx)
            ctx[self.name] = value