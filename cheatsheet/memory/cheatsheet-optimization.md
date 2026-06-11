---
name: cheatsheet-optimization
description: 用户后续复习各章节时会回来优化 cheatsheet，需要持续改进
metadata:
  type: project
---

用户会在复习离散数学各章节时，回到 Claude Code 对 `cheatsheet/cheatsheet.tex` 进行针对性优化。

**Why:** 用户正在备考离散数学(2)，cheatsheet 是核心复习资料，需要随着复习进度不断完善。

**How to apply:**
- 当用户提到某个具体章节/定理/概念时，主动询问是否需要同步更新 cheatsheet
- cheatsheet 偏好：重点写定理、易错概念、tricky 选择题考点；不写例题
- 风格：紧凑（3栏、小字号）、精确、强调易错点
- 编译命令：`cd cheatsheet && latexmk -pdf -xelatex cheatsheet.tex`
- 课件在 `课件/` 目录，如需读取 PDF 先 `pdftotext -layout -enc UTF-8` 转换
