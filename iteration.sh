#!/usr/bin/env bash
# 同步已经编辑好的项目文件，可由外部定时任务调用。
set -euo pipefail

CDPATH= cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")"
# Git 钩子可能继承调用方的工作树和索引位置。
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR

if [[ ! -e .git || -n "$(git rev-parse --show-prefix)" ]] ||
   ! git ls-files --error-unmatch -- iteration.sh >/dev/null ||
   ! git grep -q -E '^name:[[:blank:]]*mao-wisdom[[:space:]]*$' HEAD -- SKILL.md; then
    echo "请在本项目的 Git 工作树根目录运行 iteration.sh。" >&2
    exit 1
fi

if [[ "$(git symbolic-ref --quiet --short HEAD)" != main ]]; then
    echo "只有 main 分支可以运行自动同步。" >&2
    exit 1
fi
git remote get-url --push origin >/dev/null

# 冲突文件的 git add 会被 Git 当作人工解决。先检查整个工作树的操作状态。
for state in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply sequencer; do
    if [[ -e "$(git rev-parse --git-path "$state")" ]]; then
        echo "Git 操作尚在进行（$state），请处理后再同步。" >&2
        exit 1
    fi
done
if [[ -n "$(git ls-files --unmerged)" ]]; then
    echo "工作树包含未解决的冲突，请处理后再同步。" >&2
    exit 1
fi

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" | tee -a iteration.log
}

trap 'log "同步失败，请查看上方 Git 错误。" >&2' ERR
docs=':(glob)references/**/*.md'
files=(.gitattributes .gitignore README.md SKILL.md iteration.sh scripts/search_quotes.py
       scripts/fulltext.py tests/test_search_quotes.py tests/test_fulltext.py tests/test_sync.py "$docs")

# 先检查候选文档，再做任何暂存。SQLite 等二进制文件即使用 .md 命名也不会提交。
git ls-files -z --cached --others --exclude-standard -- "$docs" |
    while IFS= read -r -d '' doc; do
        if [[ -L "$doc" || ( -e "$doc" && ! -f "$doc" ) ]]; then
            printf '资料文件须为普通文本文件：%s\n' "$doc" >&2
            exit 1
        fi
        [[ -f "$doc" ]] || continue  # 已删除的文档可以同步
        if IFS= read -r -d '' _ < "$doc"; then
            printf '资料目录中发现二进制文件：%s\n' "$doc" >&2
            exit 1
        fi
    done

# ls-files 会列出受管文件和新文件，并尊重 .gitignore。NUL 分隔可保留文件名中的空格和换行。
git ls-files -z --cached --others --exclude-standard -- "${files[@]}" |
    git --literal-pathspecs add -A --pathspec-from-file=- --pathspec-file-nul

if ! git diff --cached --quiet -- "${files[@]}"; then
    # --only 保留项目范围以外已经暂存的改动。
    git diff --cached --no-renames --name-only -z -- "${files[@]}" |
        git --literal-pathspecs commit --only --pathspec-from-file=- --pathspec-file-nul \
            -m "更新智慧宝库项目内容 [$(date '+%Y-%m-%d %H:%M')]"
fi

# 如果上次提交成功而推送失败，即使工作树干净也要重试。
if git rev-parse --verify --quiet refs/remotes/origin/main >/dev/null &&
   git merge-base --is-ancestor HEAD refs/remotes/origin/main; then
    log "没有待推送的本地提交。"
    exit 0
fi

git -c push.followTags=false push origin refs/heads/main:refs/heads/main
log "已推送到 origin/main。"
