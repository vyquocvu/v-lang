"""
LLVM IR code generation visitor for the vlang compiler.

``CodeGenVisitor`` walks the pure-data AST defined in ``vlang.nodes`` and
emits LLVM IR via an llvmlite ``IRBuilder``. Keeping emission here (rather
than on the nodes themselves) separates the AST from codegen, which makes
room for a future type-checking pass and multiple value types.

Dispatch is by node class name: a ``Foo`` node is handled by ``visit_Foo``.
The ``env`` mapping (name -> LLVM pointer / function) is threaded through
``visit`` so that nested scopes (e.g. function bodies) can use a distinct
environment without disturbing the caller's.
"""

from __future__ import annotations

from llvmlite import ir


class CodeGenVisitor:
    """Emits LLVM IR for an AST using the provided module/builder/printf."""

    def __init__(self, module: ir.Module, builder: ir.IRBuilder, printf: ir.Function) -> None:
        self.module = module
        self.builder = builder
        self.printf = printf

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def generate(self, node) -> None:
        """Walk *node* (typically a ``Program``) starting with a fresh scope."""
        return self.visit(node, {})

    def visit(self, node, env: dict):
        method = getattr(self, "visit_" + type(node).__name__, None)
        if method is None:
            raise NotImplementedError(f"No visitor for {type(node).__name__}")
        return method(node, env)

    # ------------------------------------------------------------------
    # Primitive nodes
    # ------------------------------------------------------------------

    def visit_Number(self, node, env):
        return ir.Constant(ir.IntType(64), int(node.value))

    def visit_Boolean(self, node, env):
        return ir.Constant(ir.IntType(1), 1 if node.value else 0)

    # ------------------------------------------------------------------
    # Binary arithmetic
    # ------------------------------------------------------------------

    def visit_Sum(self, node, env):
        return self.builder.add(self.visit(node.left, env), self.visit(node.right, env))

    def visit_Sub(self, node, env):
        return self.builder.sub(self.visit(node.left, env), self.visit(node.right, env))

    def visit_Mul(self, node, env):
        return self.builder.mul(self.visit(node.left, env), self.visit(node.right, env))

    def visit_Div(self, node, env):
        return self.builder.sdiv(self.visit(node.left, env), self.visit(node.right, env))

    def visit_Mod(self, node, env):
        return self.builder.srem(self.visit(node.left, env), self.visit(node.right, env))

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def visit_Print(self, node, env):
        value = self.visit(node.value, env)

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

    def visit_Program(self, node, env):
        for stmt in node.statements:
            self.visit(stmt, env)

    def visit_EmptyStatement(self, node, env):
        pass

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def visit_VarDecl(self, node, env):
        val = self.visit(node.expr, env)
        ptr = self.builder.alloca(val.type, name=node.name)
        self.builder.store(val, ptr)
        env[node.name] = ptr

    def visit_VarAssign(self, node, env):
        if node.name not in env:
            raise ValueError(f"Biến chưa được khai báo: {node.name}")
        ptr = env[node.name]
        val = self.visit(node.expr, env)
        self.builder.store(val, ptr)

    def visit_VarRef(self, node, env):
        if node.name not in env:
            raise ValueError(f"Biến chưa được khai báo: {node.name}")
        ptr = env[node.name]
        return self.builder.load(ptr, name=node.name)

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def visit_Compare(self, node, env):
        l_val = self.visit(node.left, env)
        r_val = self.visit(node.right, env)

        op_map = {
            "BANG": "==",
            "BANG_LON_HON": ">=",
            "BANG_NHO_HON": "<=",
            "KHAC": "!=",
            "LON_HON": ">",
            "NHO_HON": "<",
        }
        llvm_op = op_map[node.op_token]
        return self.builder.icmp_signed(llvm_op, l_val, r_val)

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------

    def visit_WhileLoop(self, node, env):
        cond_block = self.builder.append_basic_block("loop_cond")
        body_block = self.builder.append_basic_block("loop_body")
        end_block = self.builder.append_basic_block("loop_end")

        self.builder.branch(cond_block)

        self.builder.position_at_end(cond_block)
        cond_val = self.visit(node.condition, env)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0))
        self.builder.cbranch(cond_val, body_block, end_block)

        self.builder.position_at_end(body_block)
        self.visit(node.body, env)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)

        self.builder.position_at_end(end_block)

    # ------------------------------------------------------------------
    # Conditional
    # ------------------------------------------------------------------

    def visit_IfStmt(self, node, env):
        cond_val = self.visit(node.condition, env)
        if cond_val.type != ir.IntType(1):
            cond_val = self.builder.icmp_signed("!=", cond_val, ir.Constant(cond_val.type, 0))

        then_block = self.builder.append_basic_block("if_then")
        else_block = self.builder.append_basic_block("if_else") if node.else_body else None
        merge_block = self.builder.append_basic_block("if_merge")

        if else_block:
            self.builder.cbranch(cond_val, then_block, else_block)
        else:
            self.builder.cbranch(cond_val, then_block, merge_block)

        # Build then block
        self.builder.position_at_end(then_block)
        self.visit(node.then_body, env)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)

        # Build else block if it exists
        if else_block:
            self.builder.position_at_end(else_block)
            self.visit(node.else_body, env)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)

        # Position builder at merge block
        self.builder.position_at_end(merge_block)

    # ------------------------------------------------------------------
    # Functions
    # ------------------------------------------------------------------

    def visit_FuncDef(self, node, env):
        # All functions return i64 in our implementation
        func_type = ir.FunctionType(ir.IntType(64), [ir.IntType(64)] * len(node.params))
        func = ir.Function(self.module, func_type, name=node.name)
        env[node.name] = func

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

        for param_name, arg in zip(node.params, func.args):
            ptr = self.builder.alloca(ir.IntType(64), name=param_name)
            self.builder.store(arg, ptr)
            local_env[param_name] = ptr

        # Evaluate body
        self.visit(node.body, local_env)

        # Handle missing return (implicit return 0)
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(ir.IntType(64), 0))

        # Restore builder to main module block
        self.builder.position_at_end(saved_block)

    def visit_ReturnStmt(self, node, env):
        val = self.visit(node.expr, env)
        self.builder.ret(val)

    def visit_CallExpr(self, node, env):
        # Check local env first
        if node.name in env:
            func = env[node.name]
        elif node.name in self.module.globals:
            func = self.module.get_global(node.name)
        else:
            raise ValueError(f"Hàm chưa được định nghĩa: {node.name}")

        arg_vals = []
        for arg in node.args:
            val = self.visit(arg, env)
            if isinstance(val.type, ir.PointerType):
                val = self.builder.ptrtoint(val, ir.IntType(64))
            arg_vals.append(val)
        return self.builder.call(func, arg_vals)

    # ------------------------------------------------------------------
    # Arrays
    # ------------------------------------------------------------------

    def visit_ArrayLiteral(self, node, env):
        size = len(node.elements)
        # Default to i64 if empty
        elem_type = ir.IntType(64)
        if size > 0:
            first_val = self.visit(node.elements[0], env)
            elem_type = first_val.type

        arr_type = ir.ArrayType(elem_type, size)
        # Allocate the array on the stack
        arr_alloc = self.builder.alloca(arr_type, name="array_literal")

        # Store each element
        for i, expr in enumerate(node.elements):
            val = self.visit(expr, env)
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

    def visit_ArrayIndex(self, node, env):
        arr_val = self.visit(node.array_expr, env)

        # If the array was passed as an integer parameter, cast it back to i64*
        if arr_val.type == ir.IntType(64):
            arr_ptr = self.builder.inttoptr(arr_val, ir.PointerType(ir.IntType(64)))
        else:
            arr_ptr = arr_val

        idx_val = self.visit(node.index_expr, env)
        elem_ptr = self.builder.gep(arr_ptr, [idx_val])
        return self.builder.load(elem_ptr)

    def visit_ArrayAssign(self, node, env):
        arr_val = self.visit(node.array_expr, env)

        # If the array was passed as an integer parameter, cast it back to i64*
        if arr_val.type == ir.IntType(64):
            arr_ptr = self.builder.inttoptr(arr_val, ir.PointerType(ir.IntType(64)))
        else:
            arr_ptr = arr_val

        idx_val = self.visit(node.index_expr, env)
        val = self.visit(node.value_expr, env)
        elem_ptr = self.builder.gep(arr_ptr, [idx_val])
        self.builder.store(val, elem_ptr)

    # ------------------------------------------------------------------
    # Logical operators
    # ------------------------------------------------------------------

    def visit_LogicalAnd(self, node, env):
        l_val = self.visit(node.left, env)
        r_val = self.visit(node.right, env)
        if l_val.type != ir.IntType(1):
            l_val = self.builder.icmp_signed("!=", l_val, ir.Constant(l_val.type, 0))
        if r_val.type != ir.IntType(1):
            r_val = self.builder.icmp_signed("!=", r_val, ir.Constant(r_val.type, 0))
        return self.builder.and_(l_val, r_val)

    def visit_LogicalOr(self, node, env):
        l_val = self.visit(node.left, env)
        r_val = self.visit(node.right, env)
        if l_val.type != ir.IntType(1):
            l_val = self.builder.icmp_signed("!=", l_val, ir.Constant(l_val.type, 0))
        if r_val.type != ir.IntType(1):
            r_val = self.builder.icmp_signed("!=", r_val, ir.Constant(r_val.type, 0))
        return self.builder.or_(l_val, r_val)

    # ------------------------------------------------------------------
    # Unary
    # ------------------------------------------------------------------

    def visit_UnaryMinus(self, node, env):
        val = self.visit(node.operand, env)
        return self.builder.neg(val)
