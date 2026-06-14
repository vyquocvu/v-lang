"""
Unit tests for conditionals and functions in the vlang compiler.
"""

import pytest
from llvmlite import ir

from vlang.lexer import Lexer
from vlang.parser import Parser
from vlang.nodes import (
    IfStmt,
    FuncDef,
    ReturnStmt,
    CallExpr,
    Number,
    Program,
    Compare,
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


def test_lexer_conditional_and_function_tokens():
    """Verify that conditionals and functions keywords and delimiters tokenize correctly."""
    source = "nếu x == 1 thì\n  trả_về 0\nkhác_thì\n  trả_về 1\nhết\n"
    tokens = _tokenize(source)
    types = [t[0] for t in tokens]

    assert "NEU" in types
    assert "KHAC_THI" in types
    assert "TRA_VE" in types
    assert "THI" in types
    assert "KET_THUC" in types


def test_parser_if_statement():
    """Verify that if statement parses into IfStmt node."""
    ast = _parse("nếu x == 1 thì\nin_ra(1)\nhết\n")

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    if_stmt = ast.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert isinstance(if_stmt.condition, Compare)
    assert if_stmt.else_body is None


def test_parser_if_else_statement():
    """Verify that if-else statement parses correctly."""
    ast = _parse("nếu x == 1 thì\nin_ra(1)\nkhác_thì\nin_ra(0)\nhết\n")

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    if_stmt = ast.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert if_stmt.else_body is not None
    assert isinstance(if_stmt.else_body, Program)


def test_parser_function_def_and_call():
    """Verify function definition and call parsing."""
    source = (
        "hàm cộng(a, b)\n"
        "  trả_về a + b\n"
        "hết\n"
        "in_ra(cộng(1, 2))\n"
    )
    ast = _parse(source)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 2

    func_def = ast.statements[0]
    assert isinstance(func_def, FuncDef)
    assert func_def.name == "cộng"
    assert func_def.params == ["a", "b"]

    print_stmt = ast.statements[1]
    assert isinstance(print_stmt.value, CallExpr)
    assert print_stmt.value.name == "cộng"
    assert len(print_stmt.value.args) == 2


def test_if_eval(visitor):
    """Verify that IfStmt emits correct branches in LLVM IR."""
    module = visitor.module

    # Condition: 1 == 1
    cond = Compare(Number("1"), "BANG", Number("1"))
    then_body = Program([Number("10")])
    else_body = Program([Number("20")])

    visitor.visit(IfStmt(cond, then_body, else_body), {})

    ir_text = str(module)
    assert 'label %"if_then"' in ir_text
    assert 'label %"if_else"' in ir_text
    assert "if_then:" in ir_text
    assert "if_else:" in ir_text
    assert "if_merge:" in ir_text


def test_function_eval(visitor):
    """Verify that FuncDef and CallExpr emit correct LLVM functions and calls."""
    module = visitor.module

    env = {}

    # hàm cộng(a, b) { trả_về a + b }
    from vlang.nodes import VarRef, Sum
    body = Program([ReturnStmt(Sum(VarRef("a"), VarRef("b")))])

    # Add a non-function variable to env to verify FuncDef copies only functions to local scope
    env["non_func_var"] = ir.Constant(ir.IntType(64), 42)

    visitor.visit(FuncDef("cộng", ["a", "b"], body), env)

    assert "cộng" in env
    assert isinstance(env["cộng"], ir.Function)

    # Call cộng(10, 20)
    visitor.visit(CallExpr("cộng", [Number("10"), Number("20")]), env)

    # Test looking up global function from module instead of local env
    # evaluate in empty env to force global lookup
    visitor.visit(CallExpr("cộng", [Number("30"), Number("40")]), {})

    ir_text = str(module)
    assert 'define i64 @"cộng"(i64 %".1", i64 %".2")' in ir_text
    assert 'call i64 @"cộng"(i64 10, i64 20)' in ir_text
    assert 'call i64 @"cộng"(i64 30, i64 40)' in ir_text


def test_if_eval_no_else(visitor):
    """Verify that IfStmt without else body behaves correctly."""
    module = visitor.module

    cond = Compare(Number("1"), "BANG", Number("1"))
    then_body = Program([Number("10")])

    visitor.visit(IfStmt(cond, then_body), {})

    ir_text = str(module)
    assert 'label %"if_then"' in ir_text
    assert "if_then:" in ir_text
    assert "if_merge:" in ir_text
    assert 'label %"if_else"' not in ir_text

    # Test IfStmt with terminated then block: nếu 1 thì trả_về 1 hết
    terminated_then = Program([ReturnStmt(Number("1"))])
    visitor.visit(IfStmt(cond, terminated_then), {})

    # Test IfStmt with else block and both branches terminated
    terminated_else = Program([ReturnStmt(Number("2"))])
    visitor.visit(IfStmt(cond, terminated_then, terminated_else), {})


def test_if_eval_non_i1_cond(visitor):
    """Verify that IfStmt automatically converts non-i1 conditions."""
    module = visitor.module

    # Condition is a simple Number (i64), not an i1 comparison
    cond = Number("42")
    then_body = Program([Number("10")])

    visitor.visit(IfStmt(cond, then_body), {})

    ir_text = str(module)
    # The condition should be compared to 0
    assert "icmp ne i64" in ir_text


def test_func_def_implicit_return(visitor):
    """Verify that FuncDef generates an implicit return 0 if there is no explicit return."""
    module = visitor.module

    body = Program([Number("10")])  # no return statement
    visitor.visit(FuncDef("dummy", [], body), {})

    ir_text = str(module)
    assert "ret i64 0" in ir_text


def test_call_expr_error(visitor):
    """Verify that calling an undefined function raises ValueError."""
    with pytest.raises(ValueError, match="Hàm chưa được định nghĩa: no_such_func"):
        visitor.visit(CallExpr("no_such_func", []), {})


def test_parser_empty_lists_and_empty_statements():
    """Verify that the parser correctly parses empty parameter and argument lists, and empty statements."""
    # Test function with empty param list
    ast1 = _parse("hàm test()\n  trả_về 1\nhết\n")
    assert isinstance(ast1, Program)
    func = ast1.statements[0]
    assert isinstance(func, FuncDef)
    assert func.params == []

    # Test call with empty arg list
    ast2 = _parse("in_ra(test())\n")
    assert isinstance(ast2.statements[0].value, CallExpr)
    assert ast2.statements[0].value.args == []

    # Test empty statement
    ast3 = _parse("\n")
    from vlang.nodes import EmptyStatement
    assert isinstance(ast3.statements[0], EmptyStatement)
