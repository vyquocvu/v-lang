"""
AST node classes for the vlang compiler.

Each node represents a syntactic construct in the .vpl source language.
All nodes implement an ``eval()`` method that emits LLVM IR via the
provided llvmlite builder/module.

Named ``nodes`` (not ``ast``) to avoid shadowing Python's stdlib ``ast`` module.
"""

from llvmlite import ir


# ---------------------------------------------------------------------------
# Primitive nodes
# ---------------------------------------------------------------------------

class Number:
    """An integer literal node.

    Emits an LLVM i8 constant when evaluated.
    """

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, value: str) -> None:
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self) -> ir.Constant:
        return ir.Constant(ir.IntType(64), int(self.value))


# ---------------------------------------------------------------------------
# Binary operator base class
# ---------------------------------------------------------------------------

class BinaryOp:
    """Base class for binary arithmetic operations.

    Subclasses must implement ``eval()`` and call the appropriate
    llvmlite builder method.
    """

    def __init__(
        self,
        builder: ir.IRBuilder,
        module: ir.Module,
        left: "Number | BinaryOp",
        right: "Number | BinaryOp",
    ) -> None:
        self.builder = builder
        self.module = module
        self.left = left
        self.right = right


class Sum(BinaryOp):
    """Addition: left + right  (cộng)."""

    def eval(self) -> ir.instructions.Instruction:
        return self.builder.add(self.left.eval(), self.right.eval())


class Sub(BinaryOp):
    """Subtraction: left - right  (trừ)."""

    def eval(self) -> ir.instructions.Instruction:
        return self.builder.sub(self.left.eval(), self.right.eval())


class Mul(BinaryOp):
    """Multiplication: left * right  (nhân)."""

    def eval(self) -> ir.instructions.Instruction:
        return self.builder.mul(self.left.eval(), self.right.eval())


class Div(BinaryOp):
    """Signed integer division: left / right  (chia)."""

    def eval(self) -> ir.instructions.Instruction:
        return self.builder.sdiv(self.left.eval(), self.right.eval())


# ---------------------------------------------------------------------------
# Statement nodes
# ---------------------------------------------------------------------------

class Print:
    """Print statement node: in_ra(expression).

    Calls the C ``printf`` function to output the evaluated integer value.
    """

    def __init__(
        self,
        builder: ir.IRBuilder,
        module: ir.Module,
        printf: ir.Function,
        value: "Number | BinaryOp",
    ) -> None:
        self.builder = builder
        self.module = module
        self.printf = printf
        self.value = value

    def eval(self) -> None:
        value = self.value.eval()

        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = "%i \n\0"
        c_fmt = ir.Constant(
            ir.ArrayType(ir.IntType(8), len(fmt)),
            bytearray(fmt.encode("utf8")),
        )
        if "fstr" in self.module.globals:
            global_fmt = self.module.get_global("fstr")
        else:
            global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
            global_fmt.linkage = "internal"
            global_fmt.global_constant = True
            global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)

        self.builder.call(self.printf, [fmt_arg, value])
