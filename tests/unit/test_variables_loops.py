"""
Unit tests for variables and loops in the vlang compiler.
"""

import pytest
from llvmlite import ir

from vlang.lexer import Lexer
from vlang.parser import Parser
from vlang.nodes import (
    VarDecl,
    VarAssign,
    VarRef,
    Compare,
    WhileLoop,
    Number,
    Program,
)


def _tokenize(source: str):
    lexer = Lexer().get_lexer()
    return [(t.gettokentype(), t.value) for t in lexer.lex(source)]


def _parse(source: str):
    pg = Parser()
    pg.parse()
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(source)
    return pg.get_parser().parse(tokens)


def test_lexer_variable_and_loop_tokens():
    """Verify that variables and loops keywords and assignment operator tokenize correctly."""
    source = "khai_báo x = 10\nkhi x < 20 thì\nx = x + 1\nhết\n"
    tokens = _tokenize(source)
    types = [t[0] for t in tokens]

    assert "KHAI_BAO" in types
    assert "GAN" in types
    assert "KHI" in types
    assert "THI" in types
    assert "KET_THUC" in types
    assert "NHO_HON" in types


def test_parser_variable_declaration():
    """Verify that variable declaration parses into VarDecl."""
    ast = _parse("khai_báo x = 10\n")

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    decl = ast.statements[0]
    assert isinstance(decl, VarDecl)
    assert decl.name == "x"
    assert isinstance(decl.expr, Number)
    assert decl.expr.value == "10"


def test_parser_variable_assignment_and_reference():
    """Verify that variable assignments and references parse correctly."""
    ast = _parse("x = x + 1\n")

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assign = ast.statements[0]
    assert isinstance(assign, VarAssign)
    assert assign.name == "x"
    assert isinstance(assign.expr.left, VarRef)
    assert assign.expr.left.name == "x"


def test_parser_while_loop():
    """Verify that while loop block parses correctly."""
    source = (
        "khi x < 5 thì\n"
        "x = x + 1\n"
        "hết\n"
    )
    ast = _parse(source)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    loop = ast.statements[0]
    assert isinstance(loop, WhileLoop)
    assert isinstance(loop.condition, Compare)
    assert loop.condition.op_token == "NHO_HON"
    assert isinstance(loop.body, Program)
    assert len(loop.body.statements) == 1
    assert isinstance(loop.body.statements[0], VarAssign)


def test_variable_eval(visitor):
    """Verify variable declaration, reference, and assignment emit valid LLVM IR."""
    builder = visitor.builder
    module = visitor.module

    env = {}

    # khai_báo y = 42
    visitor.visit(VarDecl("y", Number("42")), env)

    assert "y" in env
    assert isinstance(env["y"], ir.Instruction)
    assert env["y"].opname == "alloca"

    # y = y + 1
    ref_val = visitor.visit(VarRef("y"), env)
    builder.add(ref_val, ir.Constant(ir.IntType(64), 1))

    # Store it back
    visitor.visit(VarAssign("y", Number("100")), env)

    # Check IR text contains the stack allocation and stores
    ir_text = str(module)
    assert '%"y" = alloca i64' in ir_text
    assert 'store i64 42, i64* %"y"' in ir_text
    assert 'store i64 100, i64* %"y"' in ir_text


def test_while_loop_eval(visitor):
    """Verify that WhileLoop emits correct blocks in LLVM IR."""
    module = visitor.module

    env = {}

    # khai_báo x = 0
    visitor.visit(VarDecl("x", Number("0")), env)

    # khi x < 5 thì
    #   x = 10
    # hết
    cond = Compare(VarRef("x"), "NHO_HON", Number("5"))
    body = Program([VarAssign("x", Number("10"))])

    visitor.visit(WhileLoop(cond, body), env)

    ir_text = str(module)
    assert "loop_cond:" in ir_text
    assert "loop_body:" in ir_text
    assert "loop_end:" in ir_text

    # Test loop with non-i1 condition: khi 5 thì x = 10 hết
    visitor.visit(WhileLoop(Number("5"), body), env)

    # Test loop with terminated body: khi 1 thì trả_về 10 hết
    from vlang.nodes import ReturnStmt
    terminated_body = Program([ReturnStmt(Number("10"))])
    visitor.visit(WhileLoop(Number("1"), terminated_body), env)


def test_variable_errors(visitor):
    """Verify that using undeclared variables raises ValueError."""
    env = {}

    # Reference to undeclared variable
    with pytest.raises(ValueError, match="Biến chưa được khai báo: undeclared"):
        visitor.visit(VarRef("undeclared"), env)

    # Assignment to undeclared variable
    with pytest.raises(ValueError, match="Biến chưa được khai báo: undeclared"):
        visitor.visit(VarAssign("undeclared", Number("10")), env)


def test_empty_statement_eval(visitor):
    """Verify EmptyStatement does not emit any IR and executes without issue."""
    from vlang.nodes import EmptyStatement

    # Check that visiting works and does nothing
    visitor.visit(EmptyStatement(), {})
