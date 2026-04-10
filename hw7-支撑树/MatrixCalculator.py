# 这是一个交互式的矩阵计算器，支持输入、显示、加法、乘法、转置、行列式、删除行列等功能。
# 由于作业涉及的矩阵运算已经超过手算或计算器的能力范围，而互联网上的工具又不太方便使用（尤其是需要输入大矩阵时），
# 因此我让copilot实现了这个工具来辅助完成作业。它可以在命令行中运行，输入矩阵时支持纯文本和LaTeX格式，输出结果也可以显示为纯文本或LaTeX格式，方便复制到作业中。
# 具体代码由 GPT-5.3-Codex 实现，后续我对它进行了一些修改和完善。
import re
from typing import Dict, List, Optional

import numpy as np
import sympy as sp


VAR_NAMES = ["A", "B", "C", "D", "E"]
ALL_NAMES = VAR_NAMES + ["ANS"]


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
        pieces = [f"{float(x):.10g}" for x in row]
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


def require_var(store: Dict[str, Optional[np.ndarray]], name: str) -> np.ndarray:
    key = name.upper()
    if key not in ALL_NAMES:
        raise ValueError(f"Unknown variable '{name}'.")
    value = store.get(key)
    if value is None:
        raise ValueError(f"Variable {key} is empty.")
    return value


def run_repl() -> None:
    store: Dict[str, Optional[np.ndarray]] = {name: None for name in ALL_NAMES}

    print("Matrix Calculator (A-E + ANS)")
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

        try:
            if head in {"exit", "quit"}:
                break

            if head == "help":
                print(
                    "Commands:\n"
                    "  set <A|B|C|D|E>              # interactive input\n"
                    "  set <VAR> = <plain text>     # quick plain input\n"
                    "  setlatex <VAR> = <latex>     # quick latex input\n"
                    "  show <VAR>                   # show matrix + shape\n"
                    "  latex <VAR>                  # show LaTeX + shape\n"
                    "  showlatex <VAR>              # alias of latex\n"
                    "  list\n"
                    "  clear <VAR>\n"
                    "  add X Y [-> Z]\n"
                    "  mul X Y [-> Z]\n"
                    "  T X [-> Z]\n"
                    "  det X [-> Z]\n"
                    "  delrow X i [-> Z]            # delete row i (1-based)\n"
                    "  delcol X j [-> Z]            # delete col j (1-based)\n"
                    "  Variables: A B C D E ANS"
                )
                continue

            if head == "list":
                for name in ALL_NAMES:
                    m = store[name]
                    if m is None:
                        print(f"{name}: <empty>")
                    else:
                        print(f"{name}: shape={m.shape}")
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
                key = parts[1].upper()
                if key not in ALL_NAMES:
                    raise ValueError("Unknown variable.")
                store[key] = None
                print(f"{key} cleared.")
                continue

            if head == "set":
                if len(parts) >= 4 and parts[2] == "=":
                    key = parts[1].upper()
                    if key not in VAR_NAMES:
                        raise ValueError("set only supports A-E.")
                    rhs = cmd.split("=", 1)[1]
                    m = parse_plain_matrix(rhs)
                    store[key] = m
                    print_named_matrix(key, m)
                    continue

                if len(parts) != 2:
                    raise ValueError("Usage: set <A|B|C|D|E>")
                key = parts[1].upper()
                if key not in VAR_NAMES:
                    raise ValueError("set only supports A-E.")
                m = read_matrix_interactively()
                store[key] = m
                print_named_matrix(key, m)
                continue

            if head == "setlatex":
                if len(parts) < 4 or parts[2] != "=":
                    raise ValueError("Usage: setlatex <A|B|C|D|E> = <latex>")
                key = parts[1].upper()
                if key not in VAR_NAMES:
                    raise ValueError("setlatex only supports A-E.")
                rhs = cmd.split("=", 1)[1]
                m = parse_latex_matrix(rhs)
                store[key] = m
                print_named_matrix(key, m)
                continue

            if head in {"add", "mul"}:
                if len(parts) not in {3, 5}:
                    raise ValueError(f"Usage: {head} X Y [-> Z]")
                x = require_var(store, parts[1])
                y = require_var(store, parts[2])
                target = "ANS"
                if len(parts) == 5:
                    if parts[3] != "->":
                        raise ValueError("Use [-> Z] for target.")
                    target = parts[4].upper()
                    if target not in ALL_NAMES:
                        raise ValueError("Unknown target variable.")
                result = x + y if head == "add" else x @ y
                store["ANS"] = result
                store[target] = result
                print_named_matrix(target, result)
                continue

            if head == "t":
                if len(parts) not in {2, 4}:
                    raise ValueError("Usage: T X [-> Z]")
                x = require_var(store, parts[1])
                target = "ANS"
                if len(parts) == 4:
                    if parts[2] != "->":
                        raise ValueError("Use [-> Z] for target.")
                    target = parts[3].upper()
                    if target not in ALL_NAMES:
                        raise ValueError("Unknown target variable.")
                result = x.T
                store["ANS"] = result
                store[target] = result
                print_named_matrix(target, result)
                continue

            if head == "det":
                if len(parts) not in {2, 4}:
                    raise ValueError("Usage: det X [-> Z]")
                x = require_var(store, parts[1])
                if x.shape[0] != x.shape[1]:
                    raise ValueError("det requires a square matrix.")
                target = "ANS"
                if len(parts) == 4:
                    if parts[2] != "->":
                        raise ValueError("Use [-> Z] for target.")
                    target = parts[3].upper()
                    if target not in ALL_NAMES:
                        raise ValueError("Unknown target variable.")
                value = float(np.linalg.det(x))
                result = np.array([[value]], dtype=float)
                store["ANS"] = result
                store[target] = result
                print(f"{target}: shape={result.shape}")
                print(f"{target} = {value:.10g}")
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
                    if parts[3] != "->":
                        raise ValueError("Use [-> Z] for target.")
                    target = parts[4].upper()
                    if target not in ALL_NAMES:
                        raise ValueError("Unknown target variable.")

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

                store["ANS"] = result
                store[target] = result
                if len(parts) == 3:
                    print("Note: default target is ANS. Use [-> Z] to overwrite a variable.")
                print_named_matrix(target, result)
                continue

            raise ValueError("Unknown command. Type 'help'.")

        except Exception as e:
            print(f"Error: {e}")

    print("Bye.")


if __name__ == "__main__":
    run_repl()
