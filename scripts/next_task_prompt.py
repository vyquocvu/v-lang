#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    workspace_dir = Path(__file__).resolve().parents[1]
    roadmap_path = workspace_dir / "ROADMAP.md"
    
    if not roadmap_path.exists():
        print(f"Error: {roadmap_path} not found.")
        sys.exit(1)
        
    content = roadmap_path.read_text(encoding="utf-8")
    
    # Locate the first incomplete test/bug marked with 🔴
    # Typically looks like: 🔴 test_name or 🔴 07_chained.vpl
    lines = content.splitlines()
    next_task = None
    context_lines = []
    
    for i, line in enumerate(lines):
        if "🔴" in line:
            next_task = line.strip()
            # Grab some context lines around the task
            start = max(0, i - 3)
            end = min(len(lines), i + 4)
            context_lines = lines[start:end]
            break
            
    if not next_task:
        print("All tasks in ROADMAP.md are completed! 🎉")
        return

    prompt = f"""### Next TDD Task Summary (Auto-generated from ROADMAP.md)

Based on the current state of **[ROADMAP.md](file://{roadmap_path})**, the next task is:
`{next_task}`

#### Context from ROADMAP.md:
```markdown
{chr(10).join(context_lines)}
```

#### Instructions to start the next session:
1. **Target**: Support parsing multiple statements.
2. **Current failing tests to green**:
   - `test_parser.py::TestParserMultipleStatements::test_two_print_statements`
   - `test_parser.py::TestParserMultipleStatements::test_three_print_statements`
   - `test_parser.py::TestParserMultipleStatements::test_arithmetic_then_print`
   - Conformance test: `tests/conformance/programs/arithmetic/07_chained.vpl`
3. **Tasks**:
   - Update the start rule in `src/vlang/parser.py` (e.g. `program : statement_list`, `statement_list : statement_list statement | statement`).
   - Modify the AST generator / `CodeGen` to handle multiple statements in the module block or return a list of AST nodes, evaluating each sequentially.
   - Remove the `@pytest.mark.xfail` decorators from the tests in `tests/unit/test_parser.py`.
   - Remove the xfail mark for `07_chained` in `tests/conformance/test_conformance.py`.
   - Run `uv run pytest` to verify the tests pass.
"""
    print(prompt)

if __name__ == "__main__":
    main()
