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
    from vlang.codegen import CodeGen
    cg = CodeGen()
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    
    lexer = Lexer().get_lexer()
    tokens = lexer.lex("khai_báo x = 10\n")
    ast = pg.get_parser().parse(tokens)
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    decl = ast.statements[0]
    assert isinstance(decl, VarDecl)
    assert decl.name == "x"
    assert isinstance(decl.expr, Number)
    assert decl.expr.value == "10"


def test_parser_variable_assignment_and_reference():
    """Verify that variable assignments and references parse correctly."""
    from vlang.codegen import CodeGen
    cg = CodeGen()
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    
    lexer = Lexer().get_lexer()
    tokens = lexer.lex("x = x + 1\n")
    ast = pg.get_parser().parse(tokens)
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assign = ast.statements[0]
    assert isinstance(assign, VarAssign)
    assert assign.name == "x"
    assert isinstance(assign.expr.left, VarRef)
    assert assign.expr.left.name == "x"


def test_parser_while_loop():
    """Verify that while loop block parses correctly."""
    from vlang.codegen import CodeGen
    cg = CodeGen()
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    
    lexer = Lexer().get_lexer()
    source = (
        "khi x < 5 thì\n"
        "x = x + 1\n"
        "hết\n"
    )
    tokens = lexer.lex(source)
    ast = pg.get_parser().parse(tokens)
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    loop = ast.statements[0]
    assert isinstance(loop, WhileLoop)
    assert isinstance(loop.condition, Compare)
    assert loop.condition.op_token == "NHO_HON"
    assert isinstance(loop.body, Program)
    assert len(loop.body.statements) == 1
    assert isinstance(loop.body.statements[0], VarAssign)


def test_variable_eval(fresh_codegen):
    """Verify variable declaration, reference, and assignment emit valid LLVM IR."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    env = {}
    
    # khai_báo y = 42
    decl = VarDecl(builder, module, "y", Number(builder, module, "42"))
    decl.eval(env)
    
    assert "y" in env
    assert isinstance(env["y"], ir.Instruction)
    assert env["y"].opname == "alloca"
    
    # y = y + 1
    ref = VarRef(builder, module, "y")
    add = builder.add(ref.eval(env), ir.Constant(ir.IntType(64), 1))
    
    # Store it back
    assign = VarAssign(builder, module, "y", Number(builder, module, "100"))
    assign.eval(env)
    
    # Check IR text contains the stack allocation and stores
    ir_text = str(module)
    assert '%"y" = alloca i64' in ir_text
    assert 'store i64 42, i64* %"y"' in ir_text
    assert 'store i64 100, i64* %"y"' in ir_text


def test_while_loop_eval(fresh_codegen):
    """Verify that WhileLoop emits correct blocks in LLVM IR."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    env = {}
    
    # khai_báo x = 0
    VarDecl(builder, module, "x", Number(builder, module, "0")).eval(env)
    
    # khi x < 5 thì
    #   x = 10
    # hết
    cond = Compare(builder, module, VarRef(builder, module, "x"), "NHO_HON", Number(builder, module, "5"))
    body = Program(builder, module, [VarAssign(builder, module, "x", Number(builder, module, "10"))])
    
    loop = WhileLoop(builder, module, cond, body)
    loop.eval(env)
    
    ir_text = str(module)
    assert "loop_cond:" in ir_text
    assert "loop_body:" in ir_text
    assert "loop_end:" in ir_text

    # Test loop with non-i1 condition: khi 5 thì x = 10 hết
    cond_non_i1 = Number(builder, module, "5")
    loop_non_i1 = WhileLoop(builder, module, cond_non_i1, body)
    loop_non_i1.eval(env)
    
    # Test loop with terminated body: khi 1 thì trả_về 10 hết
    from vlang.nodes import ReturnStmt
    terminated_body = Program(builder, module, [ReturnStmt(builder, module, Number(builder, module, "10"))])
    loop_terminated = WhileLoop(builder, module, Number(builder, module, "1"), terminated_body)
    loop_terminated.eval(env)


def test_variable_errors(fresh_codegen):
    """Verify that using undeclared variables raises ValueError."""
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    env = {}
    
    # Reference to undeclared variable
    ref = VarRef(builder, module, "undeclared")
    with pytest.raises(ValueError, match="Biến chưa được khai báo: undeclared"):
        ref.eval(env)
        
    # Assignment to undeclared variable
    assign = VarAssign(builder, module, "undeclared", Number(builder, module, "10"))
    with pytest.raises(ValueError, match="Biến chưa được khai báo: undeclared"):
        assign.eval(env)


def test_empty_statement_eval(fresh_codegen):
    """Verify EmptyStatement does not emit any IR and executes without issue."""
    from vlang.nodes import EmptyStatement
    builder = fresh_codegen.builder
    module = fresh_codegen.module
    
    stmt = EmptyStatement(builder, module)
    # Check that calling eval works and does nothing
    stmt.eval()
