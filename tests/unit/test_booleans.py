"""
Unit tests for Boolean literals and expressions in the vlang compiler.
"""

from llvmlite import ir

from vlang.lexer import Lexer
from vlang.parser import Parser
from vlang.nodes import (
    Boolean,
    Program,
    VarDecl,
    IfStmt,
)


def _tokenize(source: str):
    lexer = Lexer().get_lexer()
    return [(t.gettokentype(), t.value) for t in lexer.lex(source)]


def _parse(source: str):
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(source)
    pg = Parser()
    pg.parse()
    ast = pg.get_parser().parse(tokens)
    if isinstance(ast, Program) and len(ast.statements) == 1:
        return ast.statements[0]
    return ast


def test_boolean_lexer_tokens():
    """Verify that boolean literals tokenize properly."""
    assert _tokenize("đúng") == [("DUNG", "đúng")]
    assert _tokenize("dung") == [("DUNG", "dung")]
    assert _tokenize("sai") == [("SAI", "sai")]


def test_boolean_parser_nodes():
    """Verify that boolean expressions parse into Boolean nodes."""
    from vlang.nodes import Print

    node_true = _parse("in_ra(đúng)\n")
    assert isinstance(node_true, Print)
    assert isinstance(node_true.value, Boolean)
    assert node_true.value.value is True

    node_false = _parse("in_ra(sai)\n")
    assert isinstance(node_false, Print)
    assert isinstance(node_false.value, Boolean)
    assert node_false.value.value is False


def test_boolean_eval(visitor):
    """Verify that visiting a Boolean node outputs LLVM i1 constants."""
    val_true = visitor.visit(Boolean(True), {})
    assert val_true.type == ir.IntType(1)
    assert val_true.constant == 1

    val_false = visitor.visit(Boolean(False), {})
    assert val_false.type == ir.IntType(1)
    assert val_false.constant == 0


def test_boolean_variable_allocation(visitor):
    """Verify that declaring a boolean variable allocates i1 on stack instead of i64."""
    module = visitor.module
    env = {}

    # khai_báo b = đúng
    visitor.visit(VarDecl("b", Boolean(True)), env)

    assert "b" in env
    assert isinstance(env["b"], ir.Instruction)
    assert env["b"].opname == "alloca"

    ir_text = str(module)
    assert '%"b" = alloca i1' in ir_text
    assert 'store i1 1, i1* %"b"' in ir_text


def test_boolean_conditional_execution(visitor):
    """Verify that IfStmt works directly with a Boolean condition without casting."""
    module = visitor.module

    # nếu đúng thì 10 hết
    cond = Boolean(True)
    then_body = Program([Boolean(False)])

    visitor.visit(IfStmt(cond, then_body), {})

    ir_text = str(module)
    # The condition is already i1, so it shouldn't generate icmp ne
    assert "icmp ne i1" not in ir_text
    assert 'br i1 1, label %"if_then", label %"if_merge"' in ir_text
