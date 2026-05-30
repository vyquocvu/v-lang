"""
CLI entry point for the vlang compiler.

Usage:
    vlang compile <source.van>              Compile to LLVM IR (output.ll)
    vlang compile <source.van> -o <name>   Compile + link to native binary
    vlang compile <source.van> --ir-only   Only emit LLVM IR (default)

Examples:
    vlang compile examples/hello.van
    vlang compile examples/hello.van -o hello
"""

import argparse
import subprocess
import sys
from pathlib import Path

from vlang.lexer import Lexer
from vlang.parser import Parser
from vlang.codegen import CodeGen


def _compile(source: Path, output_name: str | None, ir_only: bool) -> int:
    """Run the full compilation pipeline.

    Returns an exit code (0 = success).
    """
    try:
        text_input = source.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: file not found: {source}", file=sys.stderr)
        return 1

    # --- Lex ---
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(text_input)

    # --- CodeGen setup ---
    codegen = CodeGen()

    # --- Parse → emit IR ---
    pg = Parser(codegen.module, codegen.builder, codegen.printf)
    pg.parse()
    parser = pg.get_parser()

    try:
        parser.parse(tokens).eval()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    codegen.create_ir()
    ir_path = Path("output.ll")
    codegen.save_ir(str(ir_path))
    print(f"✓  LLVM IR written to {ir_path}")

    if ir_only or output_name is None:
        return 0

    # --- Link to native binary ---
    obj_path = Path("output.o")
    binary_path = Path(output_name)

    steps = [
        (["llc", "-filetype=obj", "-relocation-model=pic", str(ir_path)],
         f"llc → {obj_path}"),
        (["gcc", str(obj_path), "-o", str(binary_path)],
         f"gcc → {binary_path}"),
    ]

    for cmd, label in steps:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"error: '{' '.join(cmd)}' failed (exit {result.returncode})",
                  file=sys.stderr)
            return result.returncode
        print(f"✓  {label}")

    print(f"\n  Run: ./{binary_path}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="vlang",
        description="Vietnamese programming language compiler",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    compile_cmd = sub.add_parser("compile", help="Compile a .van source file")
    compile_cmd.add_argument("source", type=Path, help="Source file (.van)")
    compile_cmd.add_argument(
        "-o", "--output", metavar="NAME", dest="output_name",
        help="Link to a native binary with this name",
    )
    compile_cmd.add_argument(
        "--ir-only", action="store_true",
        help="Only emit LLVM IR; skip linking (default when -o is omitted)",
    )
    return ap


def main() -> None:
    ap = _build_parser()
    args = ap.parse_args()

    if args.command == "compile":
        sys.exit(_compile(args.source, args.output_name, args.ir_only))


if __name__ == "__main__":
    main()
