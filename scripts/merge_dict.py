#!/usr/bin/env python3
"""Git merge driver for KeyTao dictionaries. Rules: docs/upstream-sync.md

Usage: merge_dict.py <base> <ours> <theirs> <path>
"""
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PHRASE_DICT = "rime/keytao.phrase.dict.yaml"
SINGLE_DICT = "rime/keytao.single.dict.yaml"
ZHAI_CHARS = set("侧债宅寨择摘斋瘵砦祭窄翟")


def entry_key(line):
    if not line.strip() or line.startswith("#"):
        return None
    cols = line.split("\t")
    if len(cols) < 2:
        return None
    return (cols[0], cols[1], cols[2] if len(cols) > 2 else "")


def split_dict(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line == "...":
            return lines[: i + 1], lines[i + 1 :]
    return [], lines


def keys_of(body):
    return [k for k in map(entry_key, body) if k]


def zhai_fh_code(text, code):
    """Return the fh code of a two-char word using the qh code for zhai, else None."""
    if len(text) != 2:
        return None
    if text[0] in ZHAI_CHARS and code[:2] == "qh":
        return "fh" + code[2:]
    if text[1] in ZHAI_CHARS and code[2:4] == "qh":
        return code[:2] + "fh" + code[4:]
    return None


def merge_header(ours, theirs):
    version = next((line for line in theirs if line.startswith("version:")), None)
    if version is None:
        return ours
    return [version if line.startswith("version:") else line for line in ours]


def codes_of(keys, text):
    return "、".join(sorted(k[1] for k in keys if k[0] == text)) or "（无）"


def merge(base_text, ours_text, theirs_text, path):
    """Keep our line order and apply the upstream changes. Returns (merged_text, notes)."""
    newline = "\r\n" if "\r\n" in ours_text else "\n"
    _, base_body = split_dict(base_text.replace("\r\n", "\n"))
    ours_header, ours_body = split_dict(ours_text.replace("\r\n", "\n"))
    theirs_header, theirs_body = split_dict(theirs_text.replace("\r\n", "\n"))

    base, ours = set(keys_of(base_body)), set(keys_of(ours_body))
    theirs_lines = [(entry_key(line), line) for line in theirs_body if entry_key(line)]
    theirs = {k for k, _ in theirs_lines}
    removed = base - theirs
    kept = ours - removed
    notes = []

    # A code we gave to our word must keep ranking it first
    our_owner = {k[1]: k for k in ours - base}
    our_codes = defaultdict(set)
    for k in ours:
        our_codes[k[1]].add(k[0])
    our_words = {(k[0], k[1]) for k in ours} | {(k[0], k[1]) for k in theirs}

    after = defaultdict(list)
    anchor = None
    for key, line in theirs_lines:
        if key in kept:
            anchor = key
            continue
        if key in base or key in ours:
            continue
        text, code, weight = key
        if path == SINGLE_DICT and text in ZHAI_CHARS and code.startswith("qh"):
            notes.append(f"- zhai 单字：`{text} {code}` 上游新增，已照常接受，请确认是否改为 fh")
        fh_code = zhai_fh_code(text, code) if path == PHRASE_DICT else None
        if fh_code:
            if (text, fh_code) in our_words:
                notes.append(f"- zhai 词组：`{text} {code}` 已有 `{fh_code}`，丢弃 qh 版本")
                continue
            notes.append(f"- zhai 词组：`{text} {code}` 没有 fh 版本，改为 `{fh_code}`")
            others = "、".join(sorted(our_codes.get(fh_code, set()) - {text}))
            if others:
                notes.append(f"- 新重码：`{text} {fh_code}` 与 `{others}` 同码")
            code = fh_code
            cols = line.split("\t")
            cols[1] = code
            line = "\t".join(cols)
            key = (text, code, weight)
            our_words.add((text, code))
            if key in ours:
                continue

        place = anchor
        owner = our_owner.get(code)
        if owner and owner[0] != text:
            place = owner
            if owner[2].isdigit():
                cols = line.split("\t")
                cols[2] = str(int(owner[2]) - 1)
                line = "\t".join(cols)
            notes.append(f"- 撞码：上游新词 `{text}` 使用 `{code}`，排在你的 `{owner[0]}` 之后")
        after[place].append(line)

    merged_body = []
    pending_head = after[None]
    for line in ours_body:
        key = entry_key(line)
        if key is None:
            merged_body.append(line)
            continue
        if pending_head:
            merged_body.extend(pending_head)
            pending_head = []
        if key not in removed:
            merged_body.append(line)
            merged_body.extend(after[key])
    if pending_head:
        trailing = len(merged_body)
        while trailing and not merged_body[trailing - 1].strip():
            trailing -= 1
        merged_body[trailing:trailing] = pending_head

    merged = set(keys_of(merged_body))
    ours_touched = {k[0] for k in ours ^ base}
    theirs_touched = {k[0] for k in theirs ^ base}
    for text in sorted(ours_touched & theirs_touched):
        if {k for k in ours if k[0] == text} == {k for k in theirs if k[0] == text}:
            continue
        notes.append(
            f"- 双方都改：`{text}` 上游原为 {codes_of(base, text)}，你的 {codes_of(ours, text)}，"
            f"上游现为 {codes_of(theirs, text)}，合并为 {codes_of(merged, text)}"
        )

    lines = merge_header(ours_header, theirs_header) + merged_body
    return newline.join(lines), notes


def read_text(path):
    return Path(path).read_bytes().decode("utf-8")


def append_report(path, notes):
    if not notes:
        return
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "keytao-merge-report.md"],
        capture_output=True, text=True, check=True,
    )
    with open(result.stdout.strip(), "a", encoding="utf-8", newline="\n") as report:
        report.write(f"## {path}\n\n" + "\n".join(notes) + "\n\n")


def main():
    base_path, ours_path, theirs_path, path = sys.argv[1:5]
    merged, notes = merge(read_text(base_path), read_text(ours_path), read_text(theirs_path), path)
    Path(ours_path).write_bytes(merged.encode("utf-8"))
    append_report(path, notes)


if __name__ == "__main__":
    main()
