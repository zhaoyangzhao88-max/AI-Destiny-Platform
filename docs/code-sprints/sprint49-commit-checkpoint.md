# Sprint 49 — 提交检查点（Sprint 45-48）+ 清理测试用 venv

- **日期：** 2026-07-20
- **执行模式：** 直接执行（清理 + 提交，无判断空间）
- **范围：** 清理本轮遗留测试用虚拟环境目录，补充 `.gitignore` 规则，提交 Sprint 45-48 全部改动。**不涉及任何业务代码改动。**

---

## 第一步：venv 清理确认

执行前先确认这些目录本就不在 git 跟踪中（`git status` 不显示为 untracked，因每个 venv 内部自带 `.gitignore` 含 `*`，内容已被忽略，但根 `.gitignore` 此前并未覆盖此命名模式）。

| 目录 | 是否删除 | 说明 |
|------|----------|------|
| `venv_sprint45_test/` | ✅ 已删除 | sprint 命名，明确在清理范围 |
| `venv_sprint47_test/` | ✅ 已删除 | sprint 命名，明确在清理范围 |
| `venv_sprint48_notz/` | ✅ 已删除 | sprint 命名，明确在清理范围 |
| `venv_test/` | ⚠️ **保留，待确认** | 不在本 sprint 命名清单内。属测试用 venv（自带头 `.gitignore`），未被根 `.gitignore` 匹配，当前 `git status` 不显示。按"禁止无确认删文件"铁律，**未**擅自删除，待用户决定。 |

```text
$ for d in venv_sprint45_test venv_sprint47_test venv_sprint48_notz; do
    [ -d "$d" ] && rm -rf "$d" && echo "DELETED: $d"
  done
DELETED: venv_sprint45_test
DELETED: venv_sprint47_test
DELETED: venv_sprint48_notz

$ ls -d venv* 2>/dev/null
venv_test/
```

删除后，原 3 个目录连同其内部的嵌套 `.gitignore` 一并移除，仅剩 `venv_test/` 在磁盘上。

---

## 第二步：.gitignore 更新 diff

原根 `.gitignore` 仅有 `venv/`、`.venv/`、`env/`、`virtualenv/`，**未**覆盖 `venv_*_test/`、`venv_*_notz/` 这类临时测试环境命名。补充两条规则，防止以后再建类似临时环境被 `git status` 持续提示 untracked，也避免手滑把数百 MB 虚拟环境提交进仓库。

```diff
diff --git a/.gitignore b/.gitignore
index be91fb4..5d12f42 100644
--- a/.gitignore
+++ b/.gitignore
@@ -18,6 +18,9 @@ venv/
 .venv/
 env/
 virtualenv/
+# ---- Temporary test venvs (never commit, prevent accidental staging) ----
+venv_*_test/
+venv_*_notz/
 
 # ---- IDE / Editor ----
 .vscode/
```

> 注：本规则刻意只覆盖 `venv_*_test/` 与 `venv_*_notz/` 两种明确命名模式；
> 通配 `venv_*` 未加，以避免意外吞掉其它合法目录。`venv_test/`（无后缀 `_test`）当前不被根规则匹配，但其自带嵌套 `.gitignore` 已使其对 git 透明——如需长期忽略，建议后续单独补规则或删除该目录。

---

## 第三步：提交前最终 self_check 完整原始输出

按"提交前先跑一次最终确认，不跳过检查直接提交"铁律，`python src/core/infrastructure/bazi/engine.py` 重新运行（17 项边界案例 + 新增异常路径测试）。**退出码 0，全部通过。**

以下为 `PYTHONIOENCODING=utf-8` 下的文件化原始输出（非对话复述）：

```text
PASS 立春前年柱: 2024-02-03 12:00 -> 癸卯
PASS 立春后年柱: 2024-02-04 20:00 -> 甲辰
PASS 惊蛰前月柱: 2024-03-05 09:00 → 丙寅
PASS 惊蛰后月柱: 2024-03-05 12:00 → 丁卯
PASS 1990-08-15 12:00 年柱: 庚午
PASS 1990-08-15 12:00 月柱: 甲申
PASS 1990-08-15 12:00 日柱: 壬子
PASS 1990-08-15 12:00 时柱: 丙午
PASS 1990-08-15 12:00 日主: 壬
PASS gender=unknown 四柱/日主与 male 完全一致
PASS gender=unknown great_fortune_direction_undetermined == True
PASS gender=male great_fortune_direction_undetermined == False
PASS 乌鲁木齐02:00 真太阳时日柱(跨日回退): 辛亥
PASS 乌鲁木齐02:00 真太阳时时柱(子时): 庚子
PASS 乌鲁木齐13:00 真太阳时日柱(同日): 壬子
PASS 乌鲁木齐13:00 真太阳时时柱(巳时翻转): 乙巳
PASS 非法 timezone 显式报错: timezone='Not/A_Real_Zone' -> EngineCalculationError: 时区解析失败: timezone='Not/A_Real_Zone'。无法获取标准时区偏移，真太阳时校准无法继续。常见原因：tzdata 时区数据库未安装（pip install tzdata），或 timezone 字符串非法。原始错误: 'No time zone found with key Not/A_Real_Zone'

OK self_check: 全部通过!
```

> 第 17 项（非法 timezone 显式报错 → `EngineCalculationError`）即 Sprint 48 新增的 fail-fast 异常路径测试，证明时区解析失败时已显式报错而非静默退化为 0 修正。

---

## 第四步：提交

提交信息（与 sprint 指令一致，已落盘为 `commit_msg_s49.txt` 再用 `git commit -F` 提交以保证 UTF-8/emoji 完整）：

```text
fix: Phase 3 编码 Sprint 45-48 — 依赖声明修复 + 时区解析 fail-fast

依赖声明修复:
- Sprint 45: pyproject.toml 补充 lunar_python 依赖声明
  （全新虚拟环境验证：仅凭 pyproject.toml 可完整安装）
- Sprint 47: pyproject.toml 补充 tzdata 依赖声明
  （修复 Sprint 45 验证中暴露的 5 项 self_check 失败）

真实 bug 修复（隐藏约 5 个月，因开发机被第三方库间接带入 tzdata 而被掩盖）:
- Sprint 46: 定位根因 — 时区解析失败时静默退化为 0 修正，
  导致真太阳时校准在缺少 tzdata 的干净环境下产出错误结果
- Sprint 48: 改为 fail-fast — 新增 EngineCalculationError 领域异常，
  时区解析失败时显式报错而非静默算错；新增 self_check 测试 7
  验证异常路径；全项目 except 扫描确认无其他同类隐患

流程改进:
- 修复了'纯聊天窗口复述测试结果'的举证漏洞（Sprint 44），
  本批次全部验证均为文件化原始输出，含独立可复现的正反两面验证
  （tzdata 存在/不存在两种场景均实测）

所有代码改动均通过 self_check 验证（17项边界案例，含新增异常路径测试）。

🤖 Generated with Claude Code
```

### 提交过程中的一次修正

`git add -A` 误将临时文件 `commit_msg_s49.txt` 一并暂存，首次提交后 `git show --stat` 显示其进入树（`create mode 100644 commit_msg_s49.txt`）。该文件不应入库，遂执行：

```text
git rm --cached commit_msg_s49.txt
git commit --amend --no-edit
```

修正后提交含 11 个文件（原 12 个减去误入的 commit message 文件），`commit_msg_s49.txt` 已从树中移除。

---

## 第五步：提交结果

```text
$ git log -3 --oneline
c1c0abc fix: Phase 3 编码 Sprint 45-48 — 依赖声明修复 + 时区解析 fail-fast
6517e77 docs: Sprint 43 self_check 内容异常調査报告
5ecf923 docs+feat: Phase 3 编码 Sprint 32-41治理修复:...

$ git status
On branch master
Your branch is ahead of 'origin/master' by 1 commit.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

---

## 推送结果（"完成后上传"）

```text
$ git push origin master
To https://github.com/zhaoyangzhao88-max/AI-Destiny-Platform.git
   6517e77..c1c0abc  master -> master
```

推送成功，本地 `c1c0abc` 已同步至 `origin/master`。

---

## 遗留问题 / 建议

1. **`venv_test/` 待用户决策：** 不在本 sprint 命名清单内，按"禁止无确认删文件"铁律予以保留。如确认其为本轮遗留测试环境，建议删除或补 `venv_*` 通配规则。
2. **CRLF 换行警告：** 提交时出现多文件 "LF will be replaced by CRLF" 提示，系仓库 `core.autocrlf` 行为，非错误，不影响本次提交。如希望消除噪音可考虑统一行尾策略（另议，不在本 sprint 范围）。
