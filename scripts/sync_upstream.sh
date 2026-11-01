#!/bin/bash
set -e

cd "$(dirname "$0")/.."

UPSTREAM_REF=upstream/master
command -v python >/dev/null && PYTHON=python || PYTHON=python3

if [ -n "$(git status --porcelain)" ]; then
	echo "工作区有未提交的改动，请先提交或暂存" >&2
	exit 1
fi

git config merge.keytao-dict.name "KeyTao dictionary merge"
git config merge.keytao-dict.driver "$PYTHON scripts/merge_dict.py %O %A %B %P"
git config merge.ours.name "Always keep our version"
git config merge.ours.driver true

git fetch upstream

if git merge-base --is-ancestor "$UPSTREAM_REF" HEAD; then
	echo "已是最新"
	exit 0
fi

REPORT=$(git rev-parse --git-path keytao-merge-report.md)
rm -f "$REPORT"

git merge --no-commit --no-ff --no-edit "$UPSTREAM_REF" || true
if ! git rev-parse -q --verify MERGE_HEAD >/dev/null; then
	echo "合并未能开始，请查看上面的 git 输出" >&2
	exit 1
fi

# Files we deleted stay deleted, even when upstream modified them
git -c core.quotepath=off diff --name-only --diff-filter=U | while read -r path; do
	if ! git ls-files -u -- "$path" | grep -q "$(printf ' 2\t')"; then
		git rm -q -- "$path"
		echo "保持删除：$path"
	fi
done

echo ""
echo "改动统计（查看词条：git diff --cached HEAD -- <文件>）："
git diff --cached --stat HEAD -- rime schema

echo ""
if [ -f "$REPORT" ]; then
	cat "$REPORT"
	echo "以上条目已自动处理，可以直接修改词库再 git add"
fi

CONFLICTS=$(git -c core.quotepath=off diff --name-only --diff-filter=U)
if [ -n "$CONFLICTS" ]; then
	echo "以下文件仍有冲突，需要手动解决：" >&2
	echo "$CONFLICTS" >&2
	exit 1
fi

echo "合并完成但尚未提交，确认后运行 git commit；放弃则运行 git merge --abort"
