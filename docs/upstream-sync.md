# 同步上游词库

## 背景

这个仓库是 Rime 输入方案[星空键道6](https://github.com/xkinput/KeyTao)（remote `upstream`）的个人 fork（remote `origin`），只有一个 `master` 分支。上游的词库由机器人频繁更新，本地的改动见 `README.md`。词条的新增和修正都提交到上游，本地不长期维护自己的词。

术语：

- **词条**：词库中的一行，格式为 `词<TAB>码<TAB>权重`。
- **让码**：把短码让给更常用的词，被让的词改用更长的码。这是本地词库大部分改动的来源。
- **重码**：多个词共用一个码，靠排序决定首选和次选。
- **飞键**：不按读音取码，改用手感更好的键位，如 zhai 用 `fh`。
- **`avuio`**：顶功引导键。词的码以这些字母结尾来加长，如 `美国 mwglo` 加长为 `mwgloi`。

给 AI 工具的约束：

- 必须通过 `scripts/sync_upstream.sh` 合并，不要手动 `git merge`，也不要手工解决词库文件的冲突。
- 不要自行 `git commit` 或 `git push`，除非用户要求。推送到 `master` 且改动了 `rime/` 时，会发布手机使用的词库包。
- 不要改动报告以外的词条，除非用户要求。

```bash
# 1. 工作区要干净，手头的词库改动先提交
git status

# 2. 合并，只合并不提交
bash scripts/sync_upstream.sh

# 3. 按需查看改动
git diff --cached HEAD -- rime/keytao.phrase.dict.yaml

# 4. 想改就直接改词库，改完暂存
git add rime/keytao.phrase.dict.yaml

# 5. 确认后提交并推送，推送会触发手机词库包的发布
git commit --no-edit
git push
```

放弃这次合并：`git merge --abort`。

**终端输出**

- 改动统计：每个文件的增删行数。
- 自动处理的条目：只列需要留意的，普通的上游增删不列，要看就用第 3 步的命令。
- 仍有冲突的文件：脚本以非零状态退出，解决后 `git add`，再继续第 3 步。

报告同时写在 `.git/keytao-merge-report.md`，不入库，下次同步时覆盖。

**手动修改会保留**：合并时产生的修改和平时的修改一样，都算本地改动，之后的同步不会覆盖。比如把 `空键` 改成别的码，下次同步仍然是你的版本。

**提交之后再看**：`git diff HEAD^1 HEAD -- rime/keytao.phrase.dict.yaml`。

**让 AI 审查**：让它读 `.git/keytao-merge-report.md` 和本文档，再给出建议。在 Claude Code 里用 `! bash scripts/sync_upstream.sh` 运行，输出会同时显示给你和 AI。

## 各文件的合并方式

| 文件 | 方式 |
|---|---|
| `keytao.phrase.dict.yaml`、`keytao.single.dict.yaml` | `scripts/merge_dict.py` 按词条三方合并 |
| `keytao.css.dict.yaml`、`keytao.supplement.dict.yaml`、`keytao.symbol.dict.yaml`、`schema/desktop/keytao.schema.yaml`、`README.md` | 个人定制，始终保留本地版本 |
| 本地已删除的文件（如 `keytao-cx.dict.yaml`） | 保持删除 |
| 其他文件 | git 默认合并，有冲突时手动解决 |

## 词条合并规则

词条由 `(词, 码, 权重)` 确定，保持本地的行顺序。

1. 上游删除的词条：从本地删除。
2. 上游新增的词条：插入到它在上游文件中的前一条共有词条之后。
3. 本地的增删（让码、改权重）：始终保留。
4. 文件头：保留本地内容，`version` 取上游。

## 键道相关规则

**qh 段**：`qh` 同时是 que 和 zhai 的编码，本地去掉了 zhai 的 `qh` 码，只留 `fh`。

- zhai 字：`侧债宅寨择摘斋瘵砦祭窄翟`。
- 二字词每字两码，所以只有二字词的 `qh` 能对应到读音；三字及以上的词，码是各字首码的组合（如 `清灰冷灶 qhlz`），不受影响。
- 上游新增的二字 zhai 词：已有 `fh` 版本就丢弃 `qh` 版本，没有就把 `qh` 改成 `fh`。

**撞码**：上游新词用了本地让码后分给自己词的码时，新词的权重降低 1 并排在本地词之后，保证本地词仍是首选。

## 审查报告

合并时生成 `.git/keytao-merge-report.md`，所有条目都已自动处理，审查时只需判断结果是否合适。

| 类型 | 检查什么 |
|---|---|
| zhai 词组 | 改出的 `fh` 码是否合理；丢弃的确实是 zhai 音 |
| zhai 单字 | 只报告不改动，决定是否手动改成 `fh` |
| 撞码 | 新词是否值得单独加长一码以避开重码，加长时用 `avuio` 作为后续码 |
| 新重码 | 改出的 `fh` 码和本地哪个词同码，影响首选时调整 |
| 双方都改 | 合并结果是否保留了让码的意图，以及词是否被上游彻底删除 |

判断时优先保持本地已有的短码不变。

## 其他文件有冲突时

脚本以非零状态退出并列出文件时，先看本地相对共同祖先改了什么：

```bash
git diff "$(git merge-base HEAD MERGE_HEAD)" HEAD -- <文件>
```

以上游的新版本为基础，重新套用本地的改动意图，然后 `git add`。例如 `rime/lua/smart_2.lua` 本地只把按键从 `apostrophe` 改成 `semicolon`，上游改写文件时就用上游版本，再改回这一行。

意图不明确时交给用户决定。

## 验证

- Windows 本地没有 `rime_deployer`，推送后由 `.github/workflows/release-android.yml` 编译校验，失败时不发布。
- 校验只能发现格式和编译错误，发现不了选重和让码的问题，这些靠审查报告和实际打字确认。
- 手机词库包只打包 `rime/`，不包含 `schema/android/`。
