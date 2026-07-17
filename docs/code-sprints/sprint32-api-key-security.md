# Sprint 32 — API Key 安全管理 + git 历史泄露检查

> 执行日期：2026-07-17
> 项目路径：`E:\VSCODE\AI-Destiny-Platform`
> 范围边界：仅密钥/配置治理，不涉及任何业务代码改动

---

## 执行摘要

本 Sprint 为「确认 + 文档化」性质。经实际检查，`.gitignore` 覆盖、`.env.example`
占位模板、walking skeleton 的环境变量读取方式**均已在既往工作中就位**，本次无需
新增改动。git 历史与当前工作区均未发现任何明文密钥残留。

---

## Part A：.gitignore 覆盖确认

**实际内容（`.gitignore` 第 1–3 行）：**

```text
# --- Secrets / API keys (never commit) ---
.env
.env.local
```

**结论：** `.env` 与 `.env.local` 均已在忽略列表中（行 2、3）。✅ 无需追加。

**忽略状态验证：**

```text
$ git check-ignore .env
.env            ← .env 已被忽略（且本地当前不存在真实 .env 文件）
$ git check-ignore .env.example
（无输出）       ← .env.example 未被忽略，正确：它由产品负责人提交进 git
```

---

## Part B：本地 .env 隔离

**`.env.example` 当前内容（占位模板，不含真实值）：**

```text
DEEPSEEK_API_KEY=your_api_key_here
```

**结论：** 文件已存在且内容为规范要求的占位符，与 `docs/sprint27-walking-skeleton/`
的环境变量命名一致。✅ 无需重建。

**重要约束遵守：** 本次**未**创建包含真实 key 的 `.env` 文件。真实密钥由产品负责人
在本地手动填入 `.env`，Claude Code 不接触真实密钥。

> 注：`.env.example` 与 `.gitignore` 当前均为未跟踪状态（`git status` 显示 `??`），
> 等待产品负责人在合适的提交检查点一并纳入版本控制。

---

## Part C：git 历史泄露检查

### C-1. 全量历史扫描 `sk-`（规范指定命令）

```text
$ git log --all -p | grep -i "sk-"
+- [6. Task Breakdown](#6-task-breakdown)
...
+| TASK-01 | 实现 Task 状态机定义 ...
+| TASK-02 | 实现后台 worker 调度 ...
...
```

**判定：** 全部命中均为 `TASK-01 / TASK-02 / …` 等任务编号（"TASK-01" 中含子串
"SK-01"），属**误报**，非真实密钥。

### C-2. 全量历史扫描 20+ 位 `sk-` 密钥（额外加固校验）

```text
$ git log --all -p | grep -nE "sk-[a-zA-Z0-9]{20,}"
=== NO 20+ CHAR sk- KEY IN ANY COMMIT HISTORY ===
```

### C-3. 历史中是否提交过 `.env` 文件

```text
$ git log --all --oneline -- "*.env" ".env" ".env.local"
（无输出）

$ git log --all --oneline --diff-filter=A --name-only | grep -i "\.env"
no tracked .env ever committed
```

**结论：** 从未有任何 `.env` / `.env.local` 文件被提交进 git 历史。✅

---

## Part D：walking skeleton 读取方式确认

**`docs/sprint27-walking-skeleton/scripts/ai_interpret.py` 相关行：**

```text
28:    key = os.environ.get("DEEPSEEK_API_KEY")
31:            "ERROR: 未设置 DEEPSEEK_API_KEY 环境变量。\n"
33:            '  set DEEPSEEK_API_KEY=your_key_here\n'
35:            '  $env:DEEPSEEK_API_KEY="your_key_here"',
```

**结论：** 已采用环境变量读取（非硬编码），且在缺失时给出清晰的中/英设置指引。
可作为 Phase 3 正式代码的环境变量接入样板。✅

---

## secret 扫描（本 Sprint 必做）

### 最终工作区扫描（规范指定命令）

```text
$ grep -rn "sk-[a-zA-Z0-9]\{20,\}" . --include="*.py" --include="*.md" \
    --include="*.json" --exclude-dir=node_modules --exclude-dir=.git \
    --exclude-dir=venv_test
=== NO PLAINTEXT sk- KEY RESIDUE IN WORKING TREE ===
```

**结论：** 当前工作区无任何明文 `sk-` 密钥残留。✅

---

## 审核摘要

| 检查项 | 结果 |
|--------|------|
| `.gitignore` 覆盖 `.env` / `.env.local` | ✅ 已覆盖 |
| `.env.example` 占位模板就位 | ✅ 已就位（无真实值） |
| 真实 `.env` 文件存在/泄露 | ✅ 不存在 |
| git 历史含明文 key | ✅ 无（仅 TASK 编号误报） |
| git 历史曾提交 `.env` | ✅ 从未提交 |
| walking skeleton 环境变量读取 | ✅ 已采用 |
| 工作区明文密钥残留 | ✅ 无 |

**git 历史是否干净：** 是。无需 BFG / filter-repo 等历史重写操作。

**是否需要产品负责人做进一步处理：**

1. **无需安全处理** —— git 历史与工作区均无泄露，已确认的密钥（若有）无需紧急吊销。
2. **建议（非阻塞）：** 在下一个提交检查点，将 `.gitignore` 与 `.env.example`
   纳入版本控制（当前二者均为未跟踪状态），使 `.env` 隔离机制在团队内生效。
3. **长期纪律提醒：** 真实 `DEEPSEEK_API_KEY` 仅在本地 `.env` 中填写，且 `.env`
   已被忽略；切勿将真实值粘贴进 `.env.example` 或任何文档/代码。

---

*本 Sprint 未执行 git commit（遵守铁律）。所有改动/确认均以文档化形式交付。*
