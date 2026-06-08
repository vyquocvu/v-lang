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
    from vlang.codegen import CodeGen
    cg = CodeGen()
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    
    lexer = Lexer().get_lexer()
    tokens = lexer.lex("nếu x == 1 thì\nin_ra(1)\nhết\n")
    ast = pg.get_parser().parse(tokens)
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    if_stmt = ast.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert isinstance(if_stmt.condition, Compare)
    assert if_stmt.else_body is None


def test_parser_if_else_statement():
    """Verify that if-else statement parses correctly."""
    from vlang.codegen import CodeGen
    cg = CodeGen()
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    
    lexer = Lexer().get_lexer()
    tokens = lexer.lex("nếu x == 1 thì\nin_ra(1)\nkhác_thì\nin_ra(0)\nhết\n")
    ast = pg.get_parser().parse(tokens)
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    if_stmt = ast.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert if_stmt.else_body is not None
    assert isinstance(if_stmt.else_body, Program)


def test_parser_function_def_and_call():
    """Verify function definition and call parsing."""
    from vlang.codegen import CodeGen
    cg = CodeGen()
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    
    lexer = Lexer().get_lexer()
    source = (
        "hàm cộng(a, b)\n"
        "  trả_về a + b\n"
        "hết\n"
        "in_ra(cộng(1, 2))\n"
    )
    tokens = lexer.lex(source)
    ast = pg.get_parser().parse(tokens)
    
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


def test_if_eval(fresh_codegen):
    """Verify that IfStmt emits correct branches in LLVM IR."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    # Condition: 1 == 1
    cond = Compare(builder, module, Number(builder, module, "1"), "BANG", Number(builder, module, "1"))
    then_body = Program(builder, module, [Number(builder, module, "10")])
    else_body = Program(builder, module, [Number(builder, module, "20")])
    
    if_stmt = IfStmt(builder, module, cond, then_body, else_body)
    if_stmt.eval()
    
    ir_text = str(module)
    assert 'label %"if_then"' in ir_text
    assert 'label %"if_else"' in ir_text
    assert "if_then:" in ir_text
    assert "if_else:" in ir_text
    assert "if_merge:" in ir_text


def test_function_eval(fresh_codegen):
    """Verify that FuncDef and CallExpr emit correct LLVM functions and calls."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    env = {}
    
    # hàm cộng(a, b) { trả_về a + b }
    # Parameters and body Sum(VarRef(a), VarRef(b))
    from vlang.nodes import VarRef, Sum
    body = Program(builder, module, [ReturnStmt(builder, module, Sum(builder, module, VarRef(builder, module, "a"), VarRef(builder, module, "b")))])
    
    # Add a non-function variable to env to verify FuncDef copies only functions to local scope
    env["non_func_var"] = ir.Constant(ir.IntType(64), 42)

    func_def = FuncDef(builder, module, "cộng", ["a", "b"], body)
    func_def.eval(env)
    
    assert "cộng" in env
    assert isinstance(env["cộng"], ir.Function)
    
    # Call cộng(10, 20)
    call = CallExpr(builder, module, "cộng", [Number(builder, module, "10"), Number(builder, module, "20")])
    call.eval(env)
    
    # Test looking up global function from module instead of local env
    call_global = CallExpr(builder, module, "cộng", [Number(builder, module, "30"), Number(builder, module, "40")])
    # evaluate in empty env to force global lookup
    call_global.eval({})

    ir_text = str(module)
    assert 'define i64 @"cộng"(i64 %".1", i64 %".2")' in ir_text
    assert 'call i64 @"cộng"(i64 10, i64 20)' in ir_text
    assert 'call i64 @"cộng"(i64 30, i64 40)' in ir_text


def test_if_eval_no_else(fresh_codegen):
    """Verify that IfStmt without else body behaves correctly."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    cond = Compare(builder, module, Number(builder, module, "1"), "BANG", Number(builder, module, "1"))
    then_body = Program(builder, module, [Number(builder, module, "10")])
    
    if_stmt = IfStmt(builder, module, cond, then_body)
    if_stmt.eval()
    
    ir_text = str(module)
    assert 'label %"if_then"' in ir_text
    assert "if_then:" in ir_text
    assert "if_merge:" in ir_text
    assert 'label %"if_else"' not in ir_text

    # Test IfStmt with terminated then block: nếu 1 thì trả_về 1 hết
    from vlang.nodes import ReturnStmt
    terminated_then = Program(builder, module, [ReturnStmt(builder, module, Number(builder, module, "1"))])
    if_terminated_then = IfStmt(builder, module, cond, terminated_then)
    if_terminated_then.eval()

    # Test IfStmt with else block and both branches terminated
    terminated_else = Program(builder, module, [ReturnStmt(builder, module, Number(builder, module, "2"))])
    if_both_terminated = IfStmt(builder, module, cond, terminated_then, terminated_else)
    if_both_terminated.eval()


def test_if_eval_non_i1_cond(fresh_codegen):
    """Verify that IfStmt automatically converts non-i1 conditions."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    # Condition is a simple Number (i64), not an i1 comparison
    cond = Number(builder, module, "42")
    then_body = Program(builder, module, [Number(builder, module, "10")])
    
    if_stmt = IfStmt(builder, module, cond, then_body)
    if_stmt.eval()
    
    ir_text = str(module)
    # The condition should be compared to 0
    assert "icmp ne i64" in ir_text


def test_func_def_implicit_return(fresh_codegen):
    """Verify that FuncDef generates an implicit return 0 if there is no explicit return."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    env = {}
    body = Program(builder, module, [Number(builder, module, "10")]) # no return statement
    func_def = FuncDef(builder, module, "dummy", [], body)
    func_def.eval(env)
    
    ir_text = str(module)
    assert "ret i64 0" in ir_text


def test_call_expr_error(fresh_codegen):
    """Verify that calling an undefined function raises ValueError."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    env = {}
    call = CallExpr(builder, module, "no_such_func", [])
    with pytest.raises(ValueError, match="Hàm chưa được định nghĩa: no_such_func"):
        call.eval(env)


def test_parser_empty_lists_and_empty_statements():
    """Verify that the parser correctly parses empty parameter and argument lists, and empty statements."""
    from vlang.codegen import CodeGen
    cg = CodeGen()
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    
    lexer = Lexer().get_lexer()
    # Test function with empty param list
    tokens1 = lexer.lex("hàm test()\n  trả_về 1\nhết\n")
    ast1 = pg.get_parser().parse(tokens1)
    assert isinstance(ast1, Program)
    func = ast1.statements[0]
    assert isinstance(func, FuncDef)
    assert func.params == []
    
    # Test call with empty arg list
    tokens2 = lexer.lex("in_ra(test())\n")
    ast2 = pg.get_parser().parse(tokens2)
    assert isinstance(ast2.statements[0].value, CallExpr)
    assert ast2.statements[0].value.args == []
    
    # Test empty statement
    tokens3 = lexer.lex("\n")
    ast3 = pg.get_parser().parse(tokens3)
    from vlang.nodes import EmptyStatement
    assert isinstance(ast3.statements[0], EmptyStatement)
