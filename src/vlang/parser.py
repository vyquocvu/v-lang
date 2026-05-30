"""
LALR parser for the vlang compiler.

Uses ``rply.ParserGenerator`` to build a bottom-up parser from the token
stream produced by ``vlang.lexer.Lexer``.

Grammar (current subset):
    program    : IN_RA MO_NGOAC_TRON expression DONG_NGOAC_TRON HET_DONG
    expression : expression NHAN expression
               | expression CHIA expression
               | expression CONG expression
               | expression TRU  expression
               | SO_NGUYEN
"""

from rply import ParserGenerator
from llvmlite import ir

from vlang.nodes import Number, Sum, Sub, Print, Mul, Div

# All token names the parser may encounter.
_TOKENS = [
    "SO_NGUYEN",
    "IN_RA",
    "MO_NGOAC_TRON",
    "DONG_NGOAC_TRON",
    "HET_DONG",
    "CONG",
    "TRU",
    "NHAN",
    "CHIA",
    "IDENTIFIER",
]

# Operator precedence (low → high, left-associative by default).
_PRECEDENCE = [
    ("left", ["CONG", "TRU"]),
    ("left", ["NHAN", "CHIA"]),
]


class Parser:
    """Builds an LALR parser that emits AST nodes wired to the LLVM builder."""

    def __init__(
        self,
        module: ir.Module,
        builder: ir.IRBuilder,
        printf: ir.Function,
    ) -> None:
        self._pg = ParserGenerator(_TOKENS, precedence=_PRECEDENCE)
        self.module = module
        self.builder = builder
        self.printf = printf

    def parse(self) -> None:
        """Register all grammar productions with rply decorators."""

        @self._pg.production("program : IN_RA MO_NGOAC_TRON expression DONG_NGOAC_TRON HET_DONG")
        def program(p):
            return Print(self.builder, self.module, self.printf, p[2])

        @self._pg.production("expression : expression NHAN expression")
        @self._pg.production("expression : expression CHIA expression")
        @self._pg.production("expression : expression CONG expression")
        @self._pg.production("expression : expression TRU  expression")
        def expression(p):
            left, op, right = p[0], p[1], p[2]
            token = op.gettokentype()
            if token == "NHAN":
                return Mul(self.builder, self.module, left, right)
            if token == "CHIA":
                return Div(self.builder, self.module, left, right)
            if token == "CONG":
                return Sum(self.builder, self.module, left, right)
            if token == "TRU":
                return Sub(self.builder, self.module, left, right)
            raise ValueError(f"Unknown operator token: {token}")

        @self._pg.production("expression : SO_NGUYEN")
        def number(p):
            return Number(self.builder, self.module, p[0].value)

        @self._pg.error
        def error_handle(token):
            raise ValueError(f"Unexpected token: {token!r}")

    def get_parser(self):
        """Build and return the rply parser object."""
        return self._pg.build()
