# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Discrete Mathematics (II) homework solutions (course 24100013-0), School of Software, Tsinghua University. All LaTeX-based math proofs with accompanying C++/Python algorithm implementations.

## Build

```bash
latexmk -pdf hwX.tex    # compiles a homework .tex to PDF
```

Each `hw*/` directory contains a standalone `.tex` file with its own preamble — compile from within its directory. `latexmk` is available via TeX Live or MiKTeX.

## Python tools

- **`hw7-支撑树/MatrixCalculator.py`** — interactive matrix calculator REPL. Requires `numpy` and `sympy`. Run with `python MatrixCalculator.py`. Parses plain-text and LaTeX matrix formats; outputs numeric and LaTeX formats. Used for large matrix computations in homework.
- **`hw7-支撑树/spanning_tree.py`** — spanning tree counting via Kirchhoff's theorem (commented-out reference code for specific homework problems).

## LaTeX conventions across all `.tex` files

Every homework `.tex` uses the same preamble pattern:
- Document class: `ctexart` (Chinese article with UTF-8)
- Packages: `amsmath, amssymb, amsthm, geometry, enumitem, xcolor, mdframed, tikz`
- Geometry: `a4paper, margin=2.5cm`
- Custom theorem style (`mystyle`) with `\kaishu` font body
- `problembox` environment (gray background, rounded corners) wrapping each problem statement
- Author block: `李子嘉 2024012325`
- Compilation: use `xelatex` (required by `ctexart`)

## C++ reference implementations

- **`problems/`** — standard graph algorithms: BFS, DFS (with path tracking), Dijkstra (graph diameter), Kruskal (MST), topological sort (Kahn's algorithm), and a shortest-path-with-edge-modification variant.
- **`Chinese Postman/main.cpp`** — Hierholzer algorithm for Eulerian circuits in undirected graphs.
- All C++ files use `using namespace std;`, expect stdin input formatted as per standard competitive programming conventions.
