# 这是一个交互式的置换计算器，支持在 S_n 中进行置换的输入、显示、乘法、求逆、共轭、循环分解、对换分解等操作。
# 置换输入时可以省略第一行（1 2 3 ... n），直接输入第二行（如 "4 3 5 6 1 2"），
# 也支持轮换表示（如 "(1 2)(3 5)(4 6)" 或 "(4 6 2 3 5 1)"）。
# 输出支持纯文本和 LaTeX 两种格式，方便复制到作业中。
# 由 Claude Code 根据用户需求实现，风格参照 hw7 中的 MatrixCalculator.py。
import re
import sys
from typing import Dict, List, Optional, Tuple

# 修正 Windows 终端 UTF-8 编码问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ========================= 置换核心类 =========================


class Permutation:
    """S_n 中的一个置换。内部用 1-indexed 列表表示：mapping[i-1] = 元素 i 的像。"""

    def __init__(self, mapping: List[int]):
        """
        mapping: 长度为 n 的列表，mapping[i] = 元素 (i+1) 映射到的值（1-indexed）。
        例如 [4, 3, 5, 6, 1, 2] 表示 1->4, 2->3, 3->5, 4->6, 5->1, 6->2。
        """
        self.n = len(mapping)
        self.mapping = list(mapping)
        self._validate()

    def _validate(self):
        if sorted(self.mapping) != list(range(1, self.n + 1)):
            raise ValueError("不是合法的置换：第二行必须是 1..n 的一个排列。")

    def image(self, x: int) -> int:
        """返回元素 x（1-indexed）在该置换下的像。"""
        return self.mapping[x - 1]

    # ---------- 群运算 ----------

    def __mul__(self, other: "Permutation") -> "Permutation":
        """
        置换乘法（标准右到左约定）：(self * other)(x) = self(other(x))，即先作用 other，再作用 self。
        对应教材中 στ 的标准定义。
        """
        if self.n != other.n:
            raise ValueError(f"无法复合不同大小的置换 (S_{self.n} vs S_{other.n})。")
        new_map = [self.image(other.image(i)) for i in range(1, self.n + 1)]
        return Permutation(new_map)

    def inverse(self) -> "Permutation":
        """返回逆置换 σ^{-1}。"""
        inv_map = [0] * self.n
        for i, v in enumerate(self.mapping):
            inv_map[v - 1] = i + 1
        return Permutation(inv_map)

    def __pow__(self, k: int) -> "Permutation":
        """置换的幂。k > 0 次幂；k = 0 返回恒等置换；k < 0 返回逆置换的 |k| 次幂。"""
        if k == 0:
            return Permutation.identity(self.n)
        if k < 0:
            return (self.inverse()) ** (-k)
        result = Permutation.identity(self.n)
        base = self
        while k:
            if k & 1:
                result = result * base
            base = base * base
            k >>= 1
        return result

    def conjugate_by(self, other: "Permutation") -> "Permutation":
        """返回 other * self * other^{-1}（用 other 共轭 self）。"""
        return other * self * other.inverse()

    # ---------- 分解 ----------

    def cycles(self) -> List[List[int]]:
        """将置换分解为不相交轮换的乘积。只返回长度 ≥ 2 的轮换。"""
        visited = [False] * self.n
        cycles = []
        for i in range(self.n):
            if not visited[i]:
                cycle = []
                j = i
                while not visited[j]:
                    visited[j] = True
                    cycle.append(j + 1)
                    j = self.mapping[j] - 1
                if len(cycle) > 1:
                    cycles.append(cycle)
        return cycles

    def to_transpositions(self) -> List[Tuple[int, int]]:
        """
        将置换表示为对换之积。
        轮换 (a1 a2 ... ak) 分解为 (a1 a2)(a2 a3)...(a_{k-1} ak)。
        """
        transps = []
        for cycle in self.cycles():
            for i in range(len(cycle) - 1):
                transps.append((cycle[i], cycle[i + 1]))
        return transps

    def sign(self) -> int:
        """返回置换的符号：1 表示偶置换，-1 表示奇置换。"""
        return 1 if len(self.to_transpositions()) % 2 == 0 else -1

    def order(self) -> int:
        """返回置换的阶（即各轮换长度的最小公倍数）。"""
        import math
        lens = [len(c) for c in self.cycles()]
        if not lens:
            return 1
        result = lens[0]
        for L in lens[1:]:
            result = result * L // math.gcd(result, L)
        return result

    # ---------- 格式化输出 ----------

    def to_bottom_row(self) -> str:
        """仅输出第二行，如 "4 3 5 6 1 2"。"""
        return " ".join(str(v) for v in self.mapping)

    def to_two_row(self) -> str:
        """输出完整的双行表示。"""
        top = " ".join(str(i) for i in range(1, self.n + 1))
        bottom = " ".join(str(v) for v in self.mapping)
        return f"[{top}]\n[{bottom}]"

    def to_latex_two_row(self) -> str:
        """输出 LaTeX 双行矩阵表示。"""
        top = " & ".join(str(i) for i in range(1, self.n + 1))
        bottom = " & ".join(str(v) for v in self.mapping)
        return f"\\begin{{bmatrix}}{top} \\\\ {bottom}\\end{{bmatrix}}"

    def to_cycle_str(self) -> str:
        """输出轮换表示，如 "(4 6 2 3 5 1)" 或 "(1 2)(3 5)(4 6)"。恒等置换输出 "e"。"""
        cycles = self.cycles()
        if not cycles:
            return "e"
        return "".join(f"({' '.join(map(str, c))})" for c in cycles)

    def to_transposition_str(self) -> str:
        """输出对换乘积表示，如 "(1 2)(2 3)(3 4)"。恒等置换输出 "e"。"""
        transps = self.to_transpositions()
        if not transps:
            return "e"
        return "".join(f"({a} {b})" for a, b in transps)

    def to_transposition_latex(self) -> str:
        """输出对换乘积的 LaTeX 形式。"""
        transps = self.to_transpositions()
        if not transps:
            return "e"
        return r"\, ".join(f"({a}\\ {b})" for a, b in transps)

    def __repr__(self):
        return f"Permutation({self.to_cycle_str()})"

    def __eq__(self, other):
        if not isinstance(other, Permutation):
            return False
        return self.n == other.n and self.mapping == other.mapping

    # ---------- 构造方法 ----------

    @staticmethod
    def identity(n: int) -> "Permutation":
        """返回 S_n 中的恒等置换。"""
        return Permutation(list(range(1, n + 1)))

    @staticmethod
    def from_bottom_row(values: List[int]) -> "Permutation":
        """从双行记法的第二行构造置换。"""
        return Permutation(values)

    @staticmethod
    def from_cycles(n: int, cycles: List[List[int]]) -> "Permutation":
        """从轮换列表构造置换。未出现的元素视为不动点。"""
        mapping = list(range(1, n + 1))
        for cycle in cycles:
            if len(cycle) == 0:
                continue
            for i in range(len(cycle)):
                a = cycle[i]
                b = cycle[(i + 1) % len(cycle)]
                mapping[a - 1] = b
        return Permutation(mapping)


# ========================= 输入解析 =========================


def parse_permutation(raw: str, n: Optional[int] = None) -> Permutation:
    """
    解析用户输入的置换。

    支持格式：
      - 双行记法（省略第一行）："4 3 5 6 1 2"
      - 轮换记法："(1 2)(3 5)(4 6)" 或 "(4 6 2 3 5 1)"
      - LaTeX 双行矩阵："\\begin{bmatrix}1 & 2 \\\\ 4 & 3\\end{bmatrix}"
    """
    text = raw.strip()
    if not text:
        raise ValueError("输入为空。")

    # 检测 LaTeX 矩阵格式
    if "\\begin" in text:
        return _parse_latex_two_row(text)

    # 检测轮换记法（包含括号）
    if "(" in text or ")" in text:
        return _parse_cycles(text, n)

    # 默认为双行记法的第二行
    return _parse_bottom_row(text)


def _parse_bottom_row(text: str) -> Permutation:
    """解析第二行输入，如 "4 3 5 6 1 2"。"""
    pieces = re.split(r"[,\s;]+", text)
    pieces = [p for p in pieces if p]
    if not pieces:
        raise ValueError("未找到有效数字。")
    values = [int(p) for p in pieces]
    return Permutation.from_bottom_row(values)


def _parse_cycles(text: str, n: Optional[int] = None) -> Permutation:
    """解析轮换记法，如 "(1 2)(3 5)(4 6)"。"""
    matches = re.findall(r"\(([^)]+)\)", text)
    if not matches:
        raise ValueError("未找到有效的轮换，请使用 (a b c) 格式。")

    cycles = []
    all_elements = set()
    for match in matches:
        pieces = re.split(r"[,\s]+", match.strip())
        pieces = [p for p in pieces if p]
        if not pieces:
            continue
        cycle = [int(p) for p in pieces]
        cycles.append(cycle)
        all_elements.update(cycle)

    if n is None:
        n = max(all_elements) if all_elements else 1

    # 验证每个元素只出现在至多一个轮换中
    if len(all_elements) != sum(len(c) for c in cycles):
        raise ValueError("轮换中的元素不能重复出现。")

    return Permutation.from_cycles(n, cycles)


def _parse_latex_two_row(text: str) -> Permutation:
    """解析 LaTeX 双行矩阵。"""
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
    if len(row_texts) < 2:
        raise ValueError("LaTeX 矩阵至少需要两行（第一行和第二行）。")

    # 第一行用于验证，第二行用于构造
    top_pieces = [p.strip() for p in row_texts[0].split("&")]
    bottom_pieces = [p.strip() for p in row_texts[1].split("&")]

    if len(top_pieces) != len(bottom_pieces):
        raise ValueError("两行长度不一致。")

    bottom_values = [int(p) for p in bottom_pieces]
    return Permutation.from_bottom_row(bottom_values)


# ========================= REPL =========================

# 变量命名规则
VAR_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

# 小写希腊字母映射（方便输入）
GREEK_NAMES = {
    "sigma": "σ",
    "tau": "τ",
    "rho": "ρ",
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ε",
    "mu": "μ",
    "nu": "ν",
    "pi": "π",
    "phi": "φ",
    "psi": "ψ",
    "omega": "ω",
}


def normalize_name(name: str) -> str:
    """规范化变量名。保留原始大小写，用于显示。"""
    key = name.strip()
    if not key:
        raise ValueError("变量名不能为空。")
    if not VAR_NAME_PATTERN.match(key):
        raise ValueError("变量名只能包含字母、数字和下划线，且以字母开头。")
    return key


def resolve_display_name(name: str) -> str:
    """将 Latin 命名解析为希腊字母显示。"""
    low = name.lower()
    return GREEK_NAMES.get(low, name)


def print_permutation_full(name: str, p: Permutation) -> None:
    """详细显示一个置换。"""
    display = resolve_display_name(name)
    sign_str = "偶置换" if p.sign() == 1 else "奇置换"
    print(f"{display} in S_{p.n}  ({sign_str},  阶 = {p.order()})")
    print(f"  双行:  {p.to_two_row()}")
    print(f"  第二行: {p.to_bottom_row()}")
    print(f"  轮换:  {p.to_cycle_str()}")
    transps = p.to_transpositions()
    if transps:
        trans_str = "".join(f"({a} {b})" for a, b in transps)
        print(f"  对换:  {trans_str}")
    else:
        print(f"  对换:  e")
    print()


def print_permutation_latex(name: str, p: Permutation) -> None:
    """以 LaTeX 格式显示置换。"""
    display = resolve_display_name(name)
    print(f"% {display} in S_{p.n}")
    print(f"% 双行表示:")
    print(p.to_latex_two_row())
    print(f"% 轮换表示: ${p.to_cycle_str()}$")
    transps = p.to_transpositions()
    if transps:
        trans_latex = r"\, ".join(f"({a}\\ {b})" for a, b in transps)
        print(f"% 对换之积: ${trans_latex}$")
    else:
        print(f"% 对换之积: $e$")
    print()


def read_multiline(prompt: str = "") -> str:
    """读取多行输入，空行结束。"""
    if prompt:
        print(prompt)
    print("输入完毕后请按两次回车（空行结束）：")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


def parse_tail_with_target(raw_tail: str) -> Tuple[str, str]:
    """解析命令尾部，提取操作数和可选的目标变量。"""
    text = raw_tail.strip()
    if not text:
        raise ValueError("缺少操作数。")
    m = re.match(r"^(.*?)(?:\s*->\s*([A-Za-z][A-Za-z0-9_]*))?\s*$", text)
    if not m:
        raise ValueError("语法错误。")
    body = (m.group(1) or "").strip()
    if not body:
        raise ValueError("缺少操作数。")
    target = m.group(2) or "ANS"
    return body, target


# ========================= REPL 辅助函数 =========================


def _parse_var_or_ans(parts: List[str], idx: int, store: dict, default_to_ans: bool) -> Tuple[str, bool]:
    """尝试将 parts[idx] 解释为变量名。若不存在且 default_to_ans，则返回 ANS。"""
    if idx >= len(parts):
        if default_to_ans:
            return "ANS", True
        raise ValueError("缺少操作数。")
    key = normalize_name(parts[idx])
    if key in store and store[key] is not None:
        return key, False
    if default_to_ans:
        return "ANS", True
    raise ValueError(f"变量 '{parts[idx]}' 未定义。")


def _parse_binary_op(parts: List[str], store: dict, op_name: str) -> Tuple[str, str, str]:
    """
    解析二元运算的参数：[X] Y [-> Z]。
    返回 (x_name, y_name, target)。
    若 X 省略则默认使用 ANS；若 -> Z 省略则 target = "ANS"。
    """
    # 去掉命令头
    args = parts[1:]

    # 找到 -> 的位置
    arrow_idx = None
    for i, a in enumerate(args):
        if a == "->":
            arrow_idx = i
            break

    if arrow_idx is not None:
        target = args[arrow_idx + 1] if arrow_idx + 1 < len(args) else "ANS"
        op_args = args[:arrow_idx]
    else:
        target = "ANS"
        op_args = args

    if len(op_args) == 1:
        # mul Y  -> X=ANS
        x_name = "ANS"
        y_name = op_args[0]
    elif len(op_args) == 2:
        x_name, y_name = op_args[0], op_args[1]
    else:
        raise ValueError(f"用法: {op_name} [X] Y [-> Z]")

    # 验证变量存在
    for name in [x_name, y_name]:
        key = normalize_name(name)
        if key not in store or store[key] is None:
            raise ValueError(f"变量 '{name}' 未定义。")

    # 确保目标变量槽位存在
    target_key = normalize_name(target)
    if target_key not in store:
        store[target_key] = None

    return x_name, y_name, target


def _parse_unary_op(parts: List[str], store: dict, op_name: str) -> Tuple[str, str]:
    """
    解析一元运算的参数：[X] [-> Z]。
    返回 (x_name, target)。
    """
    args = parts[1:]

    arrow_idx = None
    for i, a in enumerate(args):
        if a == "->":
            arrow_idx = i
            break

    if arrow_idx is not None:
        target = args[arrow_idx + 1] if arrow_idx + 1 < len(args) else "ANS"
        op_args = args[:arrow_idx]
    else:
        target = "ANS"
        op_args = args

    if len(op_args) == 0:
        x_name = "ANS"
    elif len(op_args) == 1:
        x_name = op_args[0]
    else:
        raise ValueError(f"用法: {op_name} [X] [-> Z]")

    key = normalize_name(x_name)
    if key not in store or store[key] is None:
        raise ValueError(f"变量 '{x_name}' 未定义。")

    target_key = normalize_name(target)
    if target_key not in store:
        store[target_key] = None

    return x_name, target


def _store_result(store: dict, target: str, result: Permutation) -> None:
    """将结果存入目标变量和 ANS。"""
    target_key = normalize_name(target)
    store[target_key] = result
    store["ANS"] = result


def run_repl() -> None:
    store: Dict[str, Optional[Permutation]] = {"ANS": None}
    # 预置常用变量名 (与教材一致)
    for name in ["A", "B", "C", "D", "sigma", "tau", "rho", "phi"]:
        store[name] = None

    print("=" * 60)
    print("  置换计算器  —  S_n 中的置换运算")
    print("=" * 60)
    print("支持操作：乘法、求逆、共轭、循环分解、对换分解")
    print("输入格式：第二行 \"4 3 5 6 1 2\" 或轮换 \"(1 2)(3 5)(4 6)\"")
    print("TeX 公式: 输入 \\sigma 之类的希腊字母名会自动显示为符号")
    print("键入 'help' 查看所有命令，'exit' 退出。")
    print()

    while True:
        try:
            cmd = input("perm> ").strip()
        except EOFError:
            print()
            break

        if not cmd:
            continue

        parts = cmd.split()
        head = parts[0].lower()

        # 别名
        alias = {
            "showlatex": "latex",
            "sl": "latex",
            "tr": "transpositions",
            "conj": "conjugate",
            "inv": "inverse",
            "o": "order",
        }
        head = alias.get(head, head)

        try:
            # ---------- 退出 ----------
            if head in {"exit", "quit"}:
                break

            # ---------- 帮助 ----------
            if head == "help":
                print(
                    "命令列表：\n"
                    "  （省略置换对象 X 时默认使用 ANS。）\n"
                    "\n"
                    "  —— 变量管理 ——\n"
                    "  set <VAR> [= <置换输入>]  # 交互式 / 快速赋值\n"
                    "  set <X> as <Y>             # X ← Y 的副本\n"
                    "  show [VAR]                 # 显示置换（完整信息）\n"
                    "  latex [VAR]                # 以 LaTeX 格式显示\n"
                    "  list                       # 列出所有变量\n"
                    "  clear <VAR>                # 清空变量\n"
                    "\n"
                    "  —— 置换运算 ——\n"
                    "  mul <X> <Y> [-> Z]         # 乘法 X*Y（先 Y 后 X）\n"
                    "  inv [X] [-> Z]             # 求逆 X^{-1}\n"
                    "  conj <X> <Y> [-> Z]        # 共轭 X*Y*X^{-1}\n"
                    "  pow [X] k [-> Z]           # 幂 X^k\n"
                    "  order [X]                  # 置换的阶\n"
                    "\n"
                    "  —— 分解与转换 ——\n"
                    "  cycles [X]                 # 轮换分解\n"
                    "  transpositions [X]         # 对换之积\n"
                    "  sign [X]                   # 奇偶性\n"
                    "\n"
                    "  —— 快捷输入 ——\n"
                    "  变量名 sigma / tau / rho 等会自动以希腊字母显示。\n"
                    "  输入置换时：\n"
                    "    第二行格式：    4 3 5 6 1 2\n"
                    "    轮换格式：      (4 6 2 3 5 1)\n"
                    "    多个轮换：      (1 2)(3 5)(4 6)\n"
                    "    LaTeX 双行：    \\\\begin{bmatrix} 1 & 2 \\\\\\\\ 4 & 3 \\\\end{bmatrix}\n"
                    "  提示：可省略第一行 1 2 3 ... n，直接输入第二行。"
                )
                continue

            # ---------- 列出变量 ----------
            if head == "list":
                for name in store:
                    p = store[name]
                    display = resolve_display_name(name)
                    if p is None:
                        print(f"  {display}: <空>")
                    else:
                        print(f"  {display} in S_{p.n}: {p.to_cycle_str()}")
                continue

            # ---------- 显示 ----------
            if head == "show":
                if len(parts) not in {1, 2}:
                    raise ValueError("用法: show [VAR]")
                name = "ANS" if len(parts) == 1 else parts[1]
                key = normalize_name(name)
                if key not in store or store[key] is None:
                    raise ValueError(f"变量 '{name}' 未定义。")
                print_permutation_full(name, store[key])  # type: ignore
                continue

            # ---------- LaTeX 显示 ----------
            if head == "latex":
                if len(parts) not in {1, 2}:
                    raise ValueError("用法: latex [VAR]  (别名: showlatex / sl)")
                name = "ANS" if len(parts) == 1 else parts[1]
                key = normalize_name(name)
                if key not in store or store[key] is None:
                    raise ValueError(f"变量 '{name}' 未定义。")
                print_permutation_latex(name, store[key])  # type: ignore
                continue

            # ---------- 清空 ----------
            if head == "clear":
                if len(parts) != 2:
                    raise ValueError("用法: clear <VAR>")
                key = normalize_name(parts[1])
                if key not in store:
                    raise ValueError(f"未知变量 '{parts[1]}'。")
                store[key] = None
                print(f"{resolve_display_name(parts[1])} 已清空。")
                continue

            # ---------- 赋值 ----------
            if head == "set":
                # set X as Y
                if len(parts) == 4 and parts[2].lower() == "as":
                    target_key = normalize_name(parts[1])
                    src_key = normalize_name(parts[3])
                    if src_key not in store or store[src_key] is None:
                        raise ValueError(f"源变量 '{parts[3]}' 未定义。")
                    if target_key not in store:
                        store[target_key] = None
                    store[target_key] = Permutation(list(store[src_key].mapping))  # type: ignore
                    print_permutation_full(parts[1], store[target_key])  # type: ignore
                    continue

                # set X = <perm>
                if len(parts) >= 4 and parts[2] == "=":
                    target_key = normalize_name(parts[1])
                    rhs = cmd.split("=", 1)[1].strip()
                    p = parse_permutation(rhs)
                    if target_key not in store:
                        store[target_key] = None
                    store[target_key] = p
                    print_permutation_full(parts[1], p)
                    continue

                # set X (交互式)
                if len(parts) != 2:
                    raise ValueError("用法: set <VAR> [= <置换>]  或  set <X> as <Y>")
                target_key = normalize_name(parts[1])
                if target_key not in store:
                    store[target_key] = None
                raw = read_multiline("请输入置换（第二行 或 轮换格式）：")
                p = parse_permutation(raw)
                store[target_key] = p
                print_permutation_full(parts[1], p)
                continue

            # ---------- 乘法 ----------
            if head == "mul":
                x_name, y_name, target = _parse_binary_op(parts, store, "mul")
                x = require(store, x_name)
                y = require(store, y_name)
                result = x * y
                _store_result(store, target, result)
                print(f"  -> {resolve_display_name(target)} = "
                      f"{resolve_display_name(x_name)} * {resolve_display_name(y_name)}"
                      f" = {result.to_cycle_str()}")
                print_permutation_full(target, result)
                continue

            # ---------- 求逆 ----------
            if head == "inverse":
                x_name, target = _parse_unary_op(parts, store, "inv")
                x = require(store, x_name)
                result = x.inverse()
                _store_result(store, target, result)
                print(f"  -> {resolve_display_name(target)} = ({resolve_display_name(x_name)})^{-1}"
                      f" = {result.to_cycle_str()}")
                print_permutation_full(target, result)
                continue

            # ---------- 共轭 ----------
            if head in {"conjugate", "conj"}:
                x_name, y_name, target = _parse_binary_op(parts, store, "conj")
                x = require(store, x_name)
                y = require(store, y_name)
                result = y.conjugate_by(x)
                _store_result(store, target, result)
                print(f"  -> {resolve_display_name(target)} = "
                      f"{resolve_display_name(x_name)}*{resolve_display_name(y_name)}*{resolve_display_name(x_name)}^{-1}"
                      f" = {result.to_cycle_str()}")
                print_permutation_full(target, result)
                continue

            # ---------- 幂 ----------
            if head == "pow":
                if len(parts) not in {2, 3, 4, 5}:
                    raise ValueError("用法: pow [X] k [-> Z]")

                if len(parts) in {2, 4}:
                    x = require(store, "ANS")
                    k = int(parts[1])
                    target = "ANS"
                    if len(parts) == 4 and parts[2] == "->":
                        target = parts[3]
                else:
                    x = require(store, parts[1])
                    k = int(parts[2])
                    target = "ANS"
                    if len(parts) == 5 and parts[3] == "->":
                        target = parts[4]

                result = x ** k
                target_key = normalize_name(target)
                if target_key not in store:
                    store[target_key] = None
                store[target_key] = result
                store["ANS"] = result
                src_name = parts[1] if len(parts) >= 3 else "ANS"
                print(f"  -> {resolve_display_name(target)} = ({resolve_display_name(src_name)})^{k}"
                      f" = {result.to_cycle_str()}")
                print_permutation_full(target, result)
                continue

            # ---------- 阶 ----------
            if head == "order":
                if len(parts) not in {1, 2}:
                    raise ValueError("用法: order [X]")
                x = require(store, "ANS" if len(parts) == 1 else parts[1])
                print(f"  ord = {x.order()}")
                continue

            # ---------- 轮换分解 ----------
            if head == "cycles":
                if len(parts) not in {1, 2}:
                    raise ValueError("用法: cycles [X]")
                x = require(store, "ANS" if len(parts) == 1 else parts[1])
                print(f"  轮换分解: {x.to_cycle_str()}")
                cycles = x.cycles()
                if cycles:
                    for c in cycles:
                        print(f"    {c}  (长度 {len(c)})")
                else:
                    print(f"    (恒等置换)")
                continue

            # ---------- 对换分解 ----------
            if head == "transpositions":
                if len(parts) not in {1, 2}:
                    raise ValueError("用法: transpositions [X]  (别名: tr)")
                x = require(store, "ANS" if len(parts) == 1 else parts[1])
                transps = x.to_transpositions()
                if transps:
                    trans_str = "".join(f"({a} {b})" for a, b in transps)
                    print(f"  对换之积: {trans_str}")
                    print(f"  对换个数: {len(transps)}")
                    print(f"  奇偶性: {'偶置换' if x.sign() == 1 else '奇置换'}")
                else:
                    print(f"  对换之积: e")
                    print(f"  对换个数: 0")
                    print(f"  奇偶性: 偶置换")
                continue

            # ---------- 奇偶性 ----------
            if head == "sign":
                if len(parts) not in {1, 2}:
                    raise ValueError("用法: sign [X]")
                x = require(store, "ANS" if len(parts) == 1 else parts[1])
                print(f"  sgn = {x.sign():+d}  ({'偶置换' if x.sign()==1 else '奇置换'})")
                continue

            # ---------- 未知命令 ----------
            print(f"未知命令 '{head}'。输入 'help' 查看帮助。")

        except Exception as e:
            print(f"错误: {e}")

    print("再见。")


def require(store: Dict[str, Optional[Permutation]], name: str) -> Permutation:
    """获取存储的置换，若不存在或为空则报错。"""
    key = normalize_name(name)
    if key not in store or store[key] is None:
        raise ValueError(f"变量 '{name}' 未定义或为空。")
    return store[key]  # type: ignore


# ========================= 入口 =========================

if __name__ == "__main__":
    run_repl()
