# 这是一个交互式的矩阵计算器，支持输入、显示、加法、乘法、转置、行列式、删除行列等功能。
# 由于作业涉及的矩阵运算已经超过手算或计算器的能力范围，而互联网上的工具又不太方便使用（尤其是需要输入大矩阵时），
# 因此我让copilot实现了这个工具来辅助完成作业。它可以在命令行中运行，输入矩阵时支持纯文本和LaTeX格式，输出结果也可以显示为纯文本或LaTeX格式，方便复制到作业中。
# 具体代码由 GPT-5.3-Codex 实现，后续我对它进行了一些修改和完善。
import re
from typing import Dict, List, Optional

import numpy as np
import sympy as sp


DEFAULT_VAR_NAMES = ["A", "B", "C", "D", "E"]
VAR_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
SYSTEM_NAMES = {"I"}
LATEX_ZERO_TOL = 1e-12


def _to_float(value: str) -> float:
    expr = value.strip()
    if not expr:
        raise ValueError("Empty value is not allowed.")
    return float(sp.N(sp.sympify(expr)))


def parse_plain_matrix(raw: str) -> np.ndarray:
    """
    Parse plain matrix text.
    Example:
      1 2 3; 4 5 6
      1,2,3
      4,5,6
    """
    text = raw.strip()
    if not text:
        raise ValueError("Input is empty.")

    if ";" in text:
        row_texts = [r.strip() for r in text.split(";") if r.strip()]
    else:
        row_texts = [r.strip() for r in text.splitlines() if r.strip()]

    if not row_texts:
        raise ValueError("No rows found.")

    matrix: List[List[float]] = []
    col_count: Optional[int] = None

    for row in row_texts:
        pieces = [p for p in re.split(r"[,\s]+", row) if p]
        values = [_to_float(p) for p in pieces]
        if col_count is None:
            col_count = len(values)
            if col_count == 0:
                raise ValueError("Row cannot be empty.")
        elif len(values) != col_count:
            raise ValueError("All rows must have the same number of columns.")
        matrix.append(values)

    return np.array(matrix, dtype=float)


def parse_latex_matrix(raw: str) -> np.ndarray:
    """
    Parse LaTeX matrix:
      \\begin{bmatrix}1 & 2 \\\\ 3 & 4\\end{bmatrix}
      \\begin{pmatrix}1 & 2 \\\\ 3 & 4\\end{pmatrix}
    """
    text = raw.strip()
    if not text:
        raise ValueError("Input is empty.")

    m = re.search(
        r"\\begin\{(?:bmatrix|pmatrix|Bmatrix|vmatrix|Vmatrix)\}(.*?)\\end\{(?:bmatrix|pmatrix|Bmatrix|vmatrix|Vmatrix)\}",
        text,
        flags=re.S,
    )
    if m:
        body = m.group(1).strip()
    else:
        body = text

    row_texts = [r.strip() for r in re.split(r"\\\\", body) if r.strip()]
    if not row_texts:
        raise ValueError("No rows found in LaTeX matrix.")

    matrix: List[List[float]] = []
    col_count: Optional[int] = None

    for row in row_texts:
        pieces = [p.strip() for p in row.split("&")]
        values = [_to_float(p) for p in pieces]
        if col_count is None:
            col_count = len(values)
            if col_count == 0:
                raise ValueError("Row cannot be empty.")
        elif len(values) != col_count:
            raise ValueError("All rows must have the same number of columns.")
        matrix.append(values)

    return np.array(matrix, dtype=float)


def format_matrix(m: np.ndarray) -> str:
    return np.array2string(m, precision=6, suppress_small=True)


def format_latex_matrix(m: np.ndarray, env: str = "bmatrix") -> str:
    rows: List[str] = []
    for row in m:
        pieces = ["0" if abs(float(x)) < LATEX_ZERO_TOL else f"{float(x):.10g}" for x in row]
        rows.append(" & ".join(pieces))
    body = r" \\ ".join(rows)
    return rf"\begin{{{env}}}{body}\end{{{env}}}"


def print_named_matrix(name: str, m: np.ndarray) -> None:
    print(f"{name}: shape={m.shape}")
    print(format_matrix(m))


def print_named_latex(name: str, m: np.ndarray) -> None:
    print(f"{name}: shape={m.shape}")
    print(format_latex_matrix(m))


def read_multiline(prompt: str = "") -> str:
    if prompt:
        print(prompt)
    print("Finish input with an empty line:")
    lines: List[str] = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


def read_matrix_interactively() -> np.ndarray:
    mode = input("Input mode [plain/latex] (default plain): ").strip().lower()
    if mode not in {"", "plain", "latex"}:
        raise ValueError("Mode must be plain or latex.")
    mode = mode or "plain"

    shape_mode = input("Specify shape first? [y/N]: ").strip().lower()
    if shape_mode == "y":
        rows = int(input("rows = ").strip())
        cols = int(input("cols = ").strip())
        data: List[List[float]] = []
        print(f"Enter {rows} rows. Use space/comma between values.")
        for i in range(rows):
            raw_row = input(f"row {i + 1}: ").strip()
            pieces = [p for p in re.split(r"[,\s]+", raw_row) if p]
            if len(pieces) != cols:
                raise ValueError(f"Expected {cols} values in row {i + 1}.")
            data.append([_to_float(p) for p in pieces])
        return np.array(data, dtype=float)

    if mode == "plain":
        raw = read_multiline("Enter plain matrix. Example: 1 2 3; 4 5 6")
        return parse_plain_matrix(raw)

    raw = read_multiline(
        r"Enter LaTeX matrix. Example: \begin{bmatrix}1 & 2 \\ 3 & 4\end{bmatrix}"
    )
    return parse_latex_matrix(raw)


def normalize_var_name(name: str) -> str:
    key = name.strip().upper()
    if not key:
        raise ValueError("Variable name cannot be empty.")
    if not VAR_NAME_PATTERN.match(key):
        raise ValueError("Invalid variable name. Use letters/numbers/underscore, and start with a letter.")
    return key


def is_reserved_var(name: str) -> bool:
    key = normalize_var_name(name)
    return key in SYSTEM_NAMES


def require_var(store: Dict[str, Optional[np.ndarray]], name: str) -> np.ndarray:
    key = normalize_var_name(name)
    if key in SYSTEM_NAMES:
        raise ValueError("I is a system identity placeholder. Use it in hcat/vcat, or generate with eye.")
    if key not in store:
        raise ValueError(f"Unknown variable '{name}'.")
    value = store.get(key)
    if value is None:
        raise ValueError(f"Variable {key} is empty.")
    return value


def try_parse_scalar(s: str) -> tuple[bool, float]:
    try:
        value = float(sp.N(sp.sympify(s.strip())))
        return True, value
    except Exception:
        return False, 0.0


def assign_var(
    store: Dict[str, Optional[np.ndarray]],
    target: str,
    value: np.ndarray,
    *,
    update_ans: bool,
    reason: str,
) -> str:
    key = normalize_var_name(target)
    store[key] = value
    if update_ans:
        store["ANS"] = value
        print(f"ANS updated ({reason}).")
    elif key == "ANS":
        print(f"ANS updated ({reason}).")
    return key


def parse_target(parts: List[str], arrow_index: int, store: Dict[str, Optional[np.ndarray]]) -> str:
    if parts[arrow_index] != "->":
        raise ValueError("Use [-> Z] for target.")
    target = normalize_var_name(parts[arrow_index + 1])
    if target != "ANS" and target not in store:
        store[target] = None
    return target


def parse_order_with_optional_target(
    args: List[str],
    expected_len: int,
    store: Dict[str, Optional[np.ndarray]],
) -> tuple[List[int], str]:
    target = "ANS"
    order_args = args
    if "->" in args:
        arrow_pos = args.index("->")
        if arrow_pos != len(args) - 2:
            raise ValueError("Usage: ... <order...> [-> Z]")
        target = parse_target(args, arrow_pos, store)
        order_args = args[:arrow_pos]

    if not order_args:
        raise ValueError("Need at least one index.")

    try:
        order = [int(x) for x in order_args]
    except ValueError as e:
        raise ValueError("Order indices must be integers.") from e

    if len(order) != len(set(order)):
        raise ValueError("Order indices must not be duplicated.")

    if any(i < 1 or i > expected_len for i in order):
        raise ValueError(f"All indices must be in range 1..{expected_len}.")

    return order, target


def parse_tail_with_optional_target(
    raw_tail: str,
    store: Dict[str, Optional[np.ndarray]],
) -> tuple[str, str]:
    text = raw_tail.strip()
    if not text:
        raise ValueError("Missing operands.")
    m = re.match(r"^(.*?)(?:\s*->\s*([A-Za-z][A-Za-z0-9_]*))?\s*$", text)
    if not m:
        raise ValueError("Invalid syntax.")
    body = (m.group(1) or "").strip()
    if not body:
        raise ValueError("Missing operands.")
    target = "ANS"
    if m.group(2):
        target = normalize_var_name(m.group(2))
        if target != "ANS" and target not in store:
            store[target] = None
    return body, target


def parse_concat_operands(body: str) -> List[str]:
    text = body.strip()
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()
    if not text:
        raise ValueError("Missing operands.")
    if "," in text:
        tokens = [t.strip() for t in text.split(",") if t.strip()]
    else:
        tokens = [t.strip() for t in text.split() if t.strip()]
    if len(tokens) < 2:
        raise ValueError("Need at least two matrices to concatenate.")
    return [normalize_var_name(t) for t in tokens]


def resolve_concat_operand(
    store: Dict[str, Optional[np.ndarray]],
    name: str,
    *,
    axis: int,
    inferred_size: Optional[int],
) -> np.ndarray:
    if name == "I":
        if inferred_size is None:
            raise ValueError("Cannot infer I size. Provide at least one non-I matrix, or use eye first.")
        return np.eye(inferred_size, dtype=float)
    return require_var(store, name)


def concat_matrices(
    store: Dict[str, Optional[np.ndarray]],
    names: List[str],
    *,
    axis: int,
) -> np.ndarray:
    if axis not in {0, 1}:
        raise ValueError("axis must be 0 or 1.")

    inferred_size: Optional[int] = None
    for n in names:
        if n == "I":
            continue
        m = require_var(store, n)
        inferred_size = m.shape[0] if axis == 1 else m.shape[1]
        break

    mats = [resolve_concat_operand(store, n, axis=axis, inferred_size=inferred_size) for n in names]
    try:
        return np.concatenate(mats, axis=axis)
    except ValueError as e:
        if axis == 1:
            raise ValueError("hcat requires all matrices to have the same row count.") from e
        raise ValueError("vcat requires all matrices to have the same column count.") from e


def run_repl() -> None:
    store: Dict[str, Optional[np.ndarray]] = {"ANS": None}
    for name in DEFAULT_VAR_NAMES:
        store[name] = None

    print("Matrix Calculator (dynamic variables + ANS)")
    print("Type 'help' for commands, 'exit' to quit.")

    while True:
        try:
            cmd = input("\nmc> ").strip()
        except EOFError:
            print()
            break

        if not cmd:
            continue

        parts = cmd.split()
        head = parts[0].lower()
        
        alias_map = {
            "tr": "t",
            "rk": "rank",
        }
        head = alias_map.get(head, head)
        
        if head == "show" and len(parts) > 1 and parts[1].lower() == "latex":
            head = "latex"
            parts = ["latex", parts[2]] if len(parts) > 2 else ["latex"]

        try:
            if head in {"exit", "quit"}:
                break

            if head == "help":
                print(
                    "Commands:\n"
                    "  set <VAR>                    # interactive input\n"
                    "  set <VAR> = <plain text>     # quick plain input\n"
                    "  setlatex <VAR> = <latex>     # quick latex input\n"
                    "  set <X> as <Y>               # X <- copy of Y (Y can be ANS)\n"
                    "  show <VAR>                   # show matrix + shape\n"
                    "  show latex <VAR>             # show matrix in LaTeX format\n"
                    "  latex <VAR>                  # show LaTeX + shape\n"
                    "  showlatex <VAR>              # alias of latex\n"
                    "  list\n"
                    "  clear <VAR>\n"
                    "  add X Y [-> Z]               # X+Y (Y can be matrix or scalar)\n"
                    "  mul X Y [-> Z]               # X*Y: scalar mult if Y is number, matmul if Y is matrix\n"
                    "  T X [-> Z]                  # or: tr X [-> Z]\n"
                    "  det X                        # output determinant\n"
                    "  inv X [-> Z]\n"
                    "  rank X                       # or: rk X; output matrix rank\n"
                    "  eye n [-> Z]                 # n x n identity matrix\n"
                    "  zeros m n [-> Z]             # m x n zero matrix\n"
                    "  ones m n [-> Z]              # m x n all-ones matrix\n"
                    "  hcat (A, I, B) [-> Z]        # horizontal concat, supports I auto-size\n"
                    "  vcat (A, I, B) [-> Z]        # vertical concat, supports I auto-size\n"
                    "  delrow X i [-> Z]            # delete row i (1-based)\n"
                    "  delcol X j [-> Z]            # delete col j (1-based)\n"
                    "  permrow X i1 i2 ... [-> Z]   # row subset/reorder by 1-based indices\n"
                    "  permcol X j1 j2 ... [-> Z]   # col subset/reorder by 1-based indices\n"
                    "  Variables: custom names (ANS is result variable, I is system identity placeholder)"
                )
                continue

            if head == "list":
                names = ["ANS"] + sorted([n for n in store.keys() if n != "ANS"])
                for name in names:
                    m = store[name]
                    if m is None:
                        print(f"{name}: <empty>")
                    else:
                        print(f"{name}: shape={m.shape}")
                print("I: <system identity placeholder>")
                continue

            if head == "show":
                if len(parts) != 2:
                    raise ValueError("Usage: show <VAR> (or: showlatex <VAR>)")
                m = require_var(store, parts[1])
                print_named_matrix(parts[1].upper(), m)
                continue

            if head in {"latex", "showlatex"}:
                if len(parts) != 2:
                    raise ValueError("Usage: latex <VAR> (alias: showlatex <VAR>)")
                m = require_var(store, parts[1])
                print_named_latex(parts[1].upper(), m)
                continue

            if head == "clear":
                if len(parts) != 2:
                    raise ValueError("Usage: clear <VAR>")
                key = normalize_var_name(parts[1])
                if key in SYSTEM_NAMES:
                    raise ValueError("Cannot clear system variable I.")
                if key not in store:
                    raise ValueError("Unknown variable.")
                store[key] = None
                print(f"{key} cleared.")
                continue

            if head == "set":
                if len(parts) == 4 and parts[2].lower() == "as":
                    target = normalize_var_name(parts[1])
                    if target in SYSTEM_NAMES:
                        raise ValueError("Cannot assign to system variable I.")
                    source = require_var(store, parts[3])
                    if target != "ANS" and target not in store:
                        store[target] = None
                    copied = np.array(source, copy=True)
                    target = assign_var(
                        store,
                        target,
                        copied,
                        update_ans=False,
                        reason=f"set {target} as {parts[3].upper()}",
                    )
                    print_named_matrix(target, copied)
                    continue

                if len(parts) >= 4 and parts[2] == "=":
                    key = normalize_var_name(parts[1])
                    if key in SYSTEM_NAMES:
                        raise ValueError("Cannot assign to system variable I.")
                    if key != "ANS" and key not in store:
                        store[key] = None
                    rhs = cmd.split("=", 1)[1]
                    m = parse_plain_matrix(rhs)
                    key = assign_var(store, key, m, update_ans=False, reason=f"set {key}")
                    print_named_matrix(key, m)
                    continue

                if len(parts) != 2:
                    raise ValueError("Usage: set <VAR>")
                key = normalize_var_name(parts[1])
                if key in SYSTEM_NAMES:
                    raise ValueError("Cannot assign to system variable I.")
                if key != "ANS" and key not in store:
                    store[key] = None
                m = read_matrix_interactively()
                key = assign_var(store, key, m, update_ans=False, reason=f"set {key}")
                print_named_matrix(key, m)
                continue

            if head == "setlatex":
                if len(parts) < 4 or parts[2] != "=":
                    raise ValueError("Usage: setlatex <VAR> = <latex>")
                key = normalize_var_name(parts[1])
                if key in SYSTEM_NAMES:
                    raise ValueError("Cannot assign to system variable I.")
                if key != "ANS" and key not in store:
                    store[key] = None
                rhs = cmd.split("=", 1)[1]
                m = parse_latex_matrix(rhs)
                key = assign_var(store, key, m, update_ans=False, reason=f"setlatex {key}")
                print_named_matrix(key, m)
                continue

            if head in {"add", "mul"}:
                if len(parts) not in {3, 5}:
                    raise ValueError(f"Usage: {head} X Y [-> Z]")
                x = require_var(store, parts[1])
                
                is_scalar, scalar_val = try_parse_scalar(parts[2])
                if is_scalar:
                    y = scalar_val
                else:
                    y = require_var(store, parts[2])
                
                target = "ANS"
                if len(parts) == 5:
                    target = parse_target(parts, 3, store)
                
                if head == "add":
                    result = x + y
                else:
                    result = x * y if is_scalar else x @ y
                
                target = assign_var(store, target, result, update_ans=True, reason=head)
                print_named_matrix(target, result)
                continue

            if head == "t":
                if len(parts) not in {2, 4}:
                    raise ValueError("Usage: T X [-> Z]")
                x = require_var(store, parts[1])
                target = "ANS"
                if len(parts) == 4:
                    target = parse_target(parts, 2, store)
                result = x.T
                target = assign_var(store, target, result, update_ans=True, reason="transpose")
                print_named_matrix(target, result)
                continue

            if head == "det":
                if len(parts) != 2:
                    raise ValueError("Usage: det X")
                x = require_var(store, parts[1])
                if x.shape[0] != x.shape[1]:
                    raise ValueError("det requires a square matrix.")
                value = float(np.linalg.det(x))
                print(f"{value:.10g}")
                continue

            if head == "inv":
                if len(parts) not in {2, 4}:
                    raise ValueError("Usage: inv X [-> Z]")
                x = require_var(store, parts[1])
                if x.shape[0] != x.shape[1]:
                    raise ValueError("inv requires a square matrix.")
                target = "ANS"
                if len(parts) == 4:
                    target = parse_target(parts, 2, store)
                try:
                    result = np.linalg.inv(x)
                except np.linalg.LinAlgError as e:
                    raise ValueError("Matrix is singular and cannot be inverted.") from e
                target = assign_var(store, target, result, update_ans=True, reason="inv")
                print_named_matrix(target, result)
                continue

            if head == "rank":
                if len(parts) != 2:
                    raise ValueError("Usage: rank X")
                x = require_var(store, parts[1])
                value = float(np.linalg.matrix_rank(x))
                print(f"{value:.10g}")
                continue

            if head == "eye":
                if len(parts) not in {2, 4}:
                    raise ValueError("Usage: eye n [-> Z]")
                n = int(parts[1])
                if n <= 0:
                    raise ValueError("n must be positive.")
                target = "ANS"
                if len(parts) == 4:
                    target = parse_target(parts, 2, store)
                if target in SYSTEM_NAMES:
                    raise ValueError("Cannot assign to system variable I.")
                result = np.eye(n, dtype=float)
                target = assign_var(store, target, result, update_ans=True, reason="eye")
                print_named_matrix(target, result)
                continue

            if head == "zeros":
                if len(parts) not in {3, 5}:
                    raise ValueError("Usage: zeros m n [-> Z]")
                m = int(parts[1])
                n = int(parts[2])
                if m <= 0 or n <= 0:
                    raise ValueError("m and n must be positive.")
                target = "ANS"
                if len(parts) == 5:
                    target = parse_target(parts, 3, store)
                if target in SYSTEM_NAMES:
                    raise ValueError("Cannot assign to system variable I.")
                result = np.zeros((m, n), dtype=float)
                target = assign_var(store, target, result, update_ans=True, reason="zeros")
                print_named_matrix(target, result)
                continue

            if head == "ones":
                if len(parts) not in {3, 5}:
                    raise ValueError("Usage: ones m n [-> Z]")
                m = int(parts[1])
                n = int(parts[2])
                if m <= 0 or n <= 0:
                    raise ValueError("m and n must be positive.")
                target = "ANS"
                if len(parts) == 5:
                    target = parse_target(parts, 3, store)
                if target in SYSTEM_NAMES:
                    raise ValueError("Cannot assign to system variable I.")
                result = np.ones((m, n), dtype=float)
                target = assign_var(store, target, result, update_ans=True, reason="ones")
                print_named_matrix(target, result)
                continue

            if head in {"delrow", "delcol"}:
                if len(parts) not in {3, 5}:
                    if head == "delrow":
                        raise ValueError("Usage: delrow X i [-> Z] (i is 1-based)")
                    raise ValueError("Usage: delcol X j [-> Z] (j is 1-based)")
                x = require_var(store, parts[1])
                idx = int(parts[2])
                target = "ANS"
                if len(parts) == 5:
                    target = parse_target(parts, 3, store)

                if head == "delrow":
                    if x.shape[0] <= 1:
                        raise ValueError("Cannot delete row: matrix must keep at least one row.")
                    if idx < 1 or idx > x.shape[0]:
                        raise ValueError(
                            f"Row index out of range: valid range is 1..{x.shape[0]} (1-based)."
                        )
                    result = np.delete(x, idx - 1, axis=0)
                else:
                    if x.shape[1] <= 1:
                        raise ValueError("Cannot delete col: matrix must keep at least one column.")
                    if idx < 1 or idx > x.shape[1]:
                        raise ValueError(
                            f"Column index out of range: valid range is 1..{x.shape[1]} (1-based)."
                        )
                    result = np.delete(x, idx - 1, axis=1)

                target = assign_var(store, target, result, update_ans=True, reason=head)
                if len(parts) == 3:
                    print("Note: default target is ANS. Use [-> Z] to overwrite a variable.")
                print_named_matrix(target, result)
                continue

            if head in {"hcat", "vcat"}:
                raw_tail = cmd[len(parts[0]):].strip()
                body, target = parse_tail_with_optional_target(raw_tail, store)
                if target in SYSTEM_NAMES:
                    raise ValueError("Cannot assign to system variable I.")
                names = parse_concat_operands(body)
                axis = 1 if head == "hcat" else 0
                result = concat_matrices(store, names, axis=axis)
                target = assign_var(store, target, result, update_ans=True, reason=head)
                print_named_matrix(target, result)
                continue

            if head in {"permrow", "permcol"}:
                if len(parts) < 4:
                    if head == "permrow":
                        raise ValueError("Usage: permrow X i1 i2 ... [-> Z]")
                    raise ValueError("Usage: permcol X j1 j2 ... [-> Z]")

                x = require_var(store, parts[1])
                expected_len = x.shape[0] if head == "permrow" else x.shape[1]
                order, target = parse_order_with_optional_target(parts[2:], expected_len, store)
                zero_based = [i - 1 for i in order]

                if head == "permrow":
                    result = x[zero_based, :]
                else:
                    result = x[:, zero_based]

                target = assign_var(store, target, result, update_ans=True, reason=head)
                print_named_matrix(target, result)
                continue

            raise ValueError("Unknown command. Type 'help'.")

        except Exception as e:
            print(f"Error: {e}")

    print("Bye.")


if __name__ == "__main__":
    run_repl()
