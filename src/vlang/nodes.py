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

    Emits an LLVM i64 constant when evaluated.
    """

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, value: str) -> None:
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self, env: dict | None = None) -> ir.Constant:
        return ir.Constant(ir.IntType(64), int(self.value))


class Boolean:
    """A boolean literal node.

    Emits an LLVM i1 constant when evaluated.
    """

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, value: bool) -> None:
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self, env: dict | None = None) -> ir.Constant:
        return ir.Constant(ir.IntType(1), 1 if self.value else 0)


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

    def eval(self, env: dict | None = None) -> ir.instructions.Instruction:
        env = env if env is not None else {}
        return self.builder.add(self.left.eval(env), self.right.eval(env))


class Sub(BinaryOp):
    """Subtraction: left - right  (trừ)."""

    def eval(self, env: dict | None = None) -> ir.instructions.Instruction:
        env = env if env is not None else {}
        return self.builder.sub(self.left.eval(env), self.right.eval(env))


class Mul(BinaryOp):
    """Multiplication: left * right  (nhân)."""

    def eval(self, env: dict | None = None) -> ir.instructions.Instruction:
        env = env if env is not None else {}
        return self.builder.mul(self.left.eval(env), self.right.eval(env))


class Div(BinaryOp):
    """Signed integer division: left / right  (chia)."""

    def eval(self, env: dict | None = None) -> ir.instructions.Instruction:
        env = env if env is not None else {}
        return self.builder.sdiv(self.left.eval(env), self.right.eval(env))


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

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}
        value = self.value.eval(env)

        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = "%i\n\0"
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


class Program:
    """A collection of statements representing a complete program."""

    def __init__(
        self,
        builder: ir.IRBuilder,
        module: ir.Module,
        statements: list | None = None,
    ) -> None:
        self.builder = builder
        self.module = module
        self.statements = statements or []

    def add_statement(self, statement) -> None:
        self.statements.append(statement)

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}
        for stmt in self.statements:
            stmt.eval(env)


class EmptyStatement:
    """An empty statement (e.g. newline or comment)."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module) -> None:
        self.builder = builder
        self.module = module

    def eval(self, env: dict | None = None) -> None:
        pass


# ---------------------------------------------------------------------------
# Variable nodes
# ---------------------------------------------------------------------------

class VarDecl:
    """Variable declaration node: khai_báo name = expr."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, name: str, expr) -> None:
        self.builder = builder
        self.module = module
        self.name = name
        self.expr = expr

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}
        val = self.expr.eval(env)
        ptr = self.builder.alloca(val.type, name=self.name)
        self.builder.store(val, ptr)
        env[self.name] = ptr


class VarAssign:
    """Variable assignment node: name = expr."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, name: str, expr) -> None:
        self.builder = builder
        self.module = module
        self.name = name
        self.expr = expr

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}
        if self.name not in env:
            raise ValueError(f"Biến chưa được khai báo: {self.name}")
        ptr = env[self.name]
        val = self.expr.eval(env)
        self.builder.store(val, ptr)


class VarRef:
    """Variable reference node: name."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, name: str) -> None:
        self.builder = builder
        self.module = module
        self.name = name

    def eval(self, env: dict | None = None) -> ir.instructions.Instruction:
        env = env if env is not None else {}
        if self.name not in env:
            raise ValueError(f"Biến chưa được khai báo: {self.name}")
        ptr = env[self.name]
        return self.builder.load(ptr, name=self.name)


# ---------------------------------------------------------------------------
# Comparison node
# ---------------------------------------------------------------------------

class Compare:
    """Comparison operator node: left op right."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, left, op_token: str, right) -> None:
        self.builder = builder
        self.module = module
        self.left = left
        self.op_token = op_token
        self.right = right

    def eval(self, env: dict | None = None) -> ir.instructions.Instruction:
        env = env if env is not None else {}
        l_val = self.left.eval(env)
        r_val = self.right.eval(env)

        op_map = {
            "BANG": "==",
            "BANG_LON_HON": ">=",
            "BANG_NHO_HON": "<=",
            "KHAC": "!=",
            "LON_HON": ">",
            "NHO_HON": "<",
        }
        llvm_op = op_map[self.op_token]
        return self.builder.icmp_signed(llvm_op, l_val, r_val)


# ---------------------------------------------------------------------------
# Loop node
# ---------------------------------------------------------------------------

class WhileLoop:
    """While loop node: khi condition thì ... hết."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, condition, body) -> None:
        self.builder = builder
        self.module = module
        self.condition = condition
        self.body = body

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}

        cond_block = self.builder.append_basic_block("loop_cond")
        body_block = self.builder.append_basic_block("loop_body")
        end_block = self.builder.append_basic_block("loop_end")

        self.builder.branch(cond_block)

        self.builder.position_at_end(cond_block)
        cond_val = self.condition.eval(env)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0))
        self.builder.cbranch(cond_val, body_block, end_block)

        self.builder.position_at_end(body_block)
        self.body.eval(env)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)

        self.builder.position_at_end(end_block)


# ---------------------------------------------------------------------------
# Conditional node
# ---------------------------------------------------------------------------

class IfStmt:
    """If statement node: nếu condition thì ... [khác_thì ...] hết."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, condition, then_body, else_body=None) -> None:
        self.builder = builder
        self.module = module
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}

        cond_val = self.condition.eval(env)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0))

        then_block = self.builder.append_basic_block("if_then")
        else_block = self.builder.append_basic_block("if_else") if self.else_body else None
        merge_block = self.builder.append_basic_block("if_merge")

        if else_block:
            self.builder.cbranch(cond_val, then_block, else_block)
        else:
            self.builder.cbranch(cond_val, then_block, merge_block)

        # Build then block
        self.builder.position_at_end(then_block)
        self.then_body.eval(env)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)

        # Build else block if it exists
        if else_block:
            self.builder.position_at_end(else_block)
            self.else_body.eval(env)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)

        # Position builder at merge block
        self.builder.position_at_end(merge_block)


# ---------------------------------------------------------------------------
# Function nodes
# ---------------------------------------------------------------------------

class FuncDef:
    """Function definition node: hàm name(params) ... hết."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, name: str, params: list[str], body) -> None:
        self.builder = builder
        self.module = module
        self.name = name
        self.params = params
        self.body = body

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}

        # All functions return i64 in our implementation
        func_type = ir.FunctionType(ir.IntType(64), [ir.IntType(64)] * len(self.params))
        func = ir.Function(self.module, func_type, name=self.name)
        env[self.name] = func

        # Build function entry
        entry_block = func.append_basic_block("entry")
        saved_block = self.builder.block

        # Switch builder position to function block
        self.builder.position_at_end(entry_block)

        # Bind parameters to stack inside a local environment scope
        local_env = {}
        for k, v in env.items():
            if isinstance(v, ir.Function):
                local_env[k] = v

        for param_name, arg in zip(self.params, func.args):
            ptr = self.builder.alloca(ir.IntType(64), name=param_name)
            self.builder.store(arg, ptr)
            local_env[param_name] = ptr

        # Evaluate body
        self.body.eval(local_env)

        # Handle missing return (implicit return 0)
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(ir.IntType(64), 0))

        # Restore builder to main module block
        self.builder.position_at_end(saved_block)


class ReturnStmt:
    """Return statement node: trả_về expr."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, expr) -> None:
        self.builder = builder
        self.module = module
        self.expr = expr

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}
        val = self.expr.eval(env)
        self.builder.ret(val)


class CallExpr:
    """Call expression node: name(args)."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, name: str, args: list) -> None:
        self.builder = builder
        self.module = module
        self.name = name
        self.args = args

    def eval(self, env: dict | None = None) -> ir.instructions.Instruction:
        env = env if env is not None else {}

        # Check local env first
        if self.name in env:
            func = env[self.name]
        elif self.name in self.module.globals:
            func = self.module.get_global(self.name)
        else:
            raise ValueError(f"Hàm chưa được định nghĩa: {self.name}")

        arg_vals = []
        for arg in self.args:
            val = arg.eval(env)
            if isinstance(val.type, ir.PointerType):
                val = self.builder.ptrtoint(val, ir.IntType(64))
            arg_vals.append(val)
        return self.builder.call(func, arg_vals)


class ArrayLiteral:
    """An array literal node: [expr1, expr2, ...].

    Allocates a fixed-size array on the stack, stores evaluated values,
    and returns a decayed pointer to the first element (i64*).
    """

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, elements: list) -> None:
        self.builder = builder
        self.module = module
        self.elements = elements

    def eval(self, env: dict | None = None) -> ir.Instruction:
        env = env if env is not None else {}
        size = len(self.elements)
        # Default to i64 if empty
        elem_type = ir.IntType(64)
        if size > 0:
            first_val = self.elements[0].eval(env)
            elem_type = first_val.type

        arr_type = ir.ArrayType(elem_type, size)
        # Allocate the array on the stack
        arr_alloc = self.builder.alloca(arr_type, name="array_literal")

        # Store each element
        for i, expr in enumerate(self.elements):
            val = expr.eval(env)
            elem_ptr = self.builder.gep(arr_alloc, [
                ir.Constant(ir.IntType(32), 0),
                ir.Constant(ir.IntType(32), i)
            ])
            self.builder.store(val, elem_ptr)

        # Decay to a pointer to the first element (i64*)
        return self.builder.gep(arr_alloc, [
            ir.Constant(ir.IntType(32), 0),
            ir.Constant(ir.IntType(32), 0)
        ])


class ArrayIndex:
    """An array indexing read node: array[index]."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, array_expr, index_expr) -> None:
        self.builder = builder
        self.module = module
        self.array_expr = array_expr
        self.index_expr = index_expr

    def eval(self, env: dict | None = None) -> ir.Instruction:
        env = env if env is not None else {}
        arr_val = self.array_expr.eval(env)
        
        # If the array was passed as an integer parameter, cast it back to i64*
        if arr_val.type == ir.IntType(64):
            arr_ptr = self.builder.inttoptr(arr_val, ir.PointerType(ir.IntType(64)))
        else:
            arr_ptr = arr_val

        idx_val = self.index_expr.eval(env)
        elem_ptr = self.builder.gep(arr_ptr, [idx_val])
        return self.builder.load(elem_ptr)


class ArrayAssign:
    """An array indexing write node: array[index] = value."""

    def __init__(self, builder: ir.IRBuilder, module: ir.Module, array_expr, index_expr, value_expr) -> None:
        self.builder = builder
        self.module = module
        self.array_expr = array_expr
        self.index_expr = index_expr
        self.value_expr = value_expr

    def eval(self, env: dict | None = None) -> None:
        env = env if env is not None else {}
        arr_val = self.array_expr.eval(env)
        
        # If the array was passed as an integer parameter, cast it back to i64*
        if arr_val.type == ir.IntType(64):
            arr_ptr = self.builder.inttoptr(arr_val, ir.PointerType(ir.IntType(64)))
        else:
            arr_ptr = arr_val

        idx_val = self.index_expr.eval(env)
        val = self.value_expr.eval(env)
        elem_ptr = self.builder.gep(arr_ptr, [idx_val])
        self.builder.store(val, elem_ptr)
