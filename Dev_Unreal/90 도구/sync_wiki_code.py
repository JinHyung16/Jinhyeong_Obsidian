# -*- coding: utf-8 -*-
"""Fills the code toggles in the Dev_Unreal notes with the current source.

A note marks a slot like this:

    <!-- code: Source/RollBall/Skill/RollBallSkillGraph.h -->
    <!-- /code -->

Everything between the two markers is replaced with a details block holding
the file as it is right now. Run this after changing the source, so the wiki
never drifts away from the code.
"""

import io
import os
import re
import sys

# Code can live in the game project or beside the notes. The tools sit
# here so the game project holds nothing but the game.
SOURCE_ROOTS = [
    r"C:\jinhyeong_project\UE5_RollBall",
    r"C:\jinhyeong_project\Jinhyeong_Obsidian\Dev_Unreal",
]
NOTES_ROOT = r"C:\jinhyeong_project\Jinhyeong_Obsidian\Dev_Unreal"

LANGUAGE_BY_SUFFIX = {
    ".h": "cpp",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".py": "python",
    ".csv": "csv",
    ".md": "markdown",
    ".ini": "ini",
}

OPEN = re.compile(r"<!-- code: ([^()<>]+?) -->")
CLOSE = "<!-- /code -->"


def block_for(relative_path):
    full = None
    for root in SOURCE_ROOTS:
        candidate = os.path.join(root, relative_path.replace("/", os.sep))
        if os.path.isfile(candidate):
            full = candidate
            break

    if full is None:
        return None, "파일 없음: " + relative_path

    text = io.open(full, encoding="utf-8-sig").read().rstrip("\n")
    language = LANGUAGE_BY_SUFFIX.get(os.path.splitext(full)[1], "")
    name = os.path.basename(full)
    lines = text.count("\n") + 1

    body = [
        "<details>",
        "<summary>%s (%d줄)</summary>" % (name, lines),
        "",
        "```" + language,
        text,
        "```",
        "",
        "</details>",
    ]
    return "\n".join(body), None


def fenced_ranges(text):
    """Character ranges inside ``` fences.

    A note that explains the marker shows it as an example inside a fence.
    Filling that one would paste a whole file into the explanation.
    """
    ranges = []
    open_at = None
    position = 0

    for line in text.splitlines(True):
        if line.lstrip().startswith("```"):
            if open_at is None:
                open_at = position
            else:
                ranges.append((open_at, position + len(line)))
                open_at = None
        position += len(line)

    if open_at is not None:
        ranges.append((open_at, len(text)))

    return ranges


def sync(note_path):
    original = io.open(note_path, encoding="utf-8").read()
    skip = fenced_ranges(original)
    out = []
    index = 0
    filled = 0
    problems = []

    while True:
        match = OPEN.search(original, index)
        if match is None:
            out.append(original[index:])
            break

        if any(start <= match.start() < end for start, end in skip):
            out.append(original[index:match.end()])
            index = match.end()
            continue

        close_at = original.find(CLOSE, match.end())
        if close_at == -1:
            problems.append("닫는 표시가 없다: " + match.group(1))
            out.append(original[index:])
            break

        block, error = block_for(match.group(1))
        if error is not None:
            problems.append(error)
            out.append(original[index:close_at])
            index = close_at
            continue

        out.append(original[index:match.end()])
        out.append("\n" + block + "\n")
        index = close_at
        filled += 1

    result = "".join(out)
    if result != original:
        io.open(note_path, "w", encoding="utf-8", newline="\n").write(result)

    return filled, problems


def main():
    if not os.path.isdir(NOTES_ROOT):
        print("노트 폴더가 없다: " + NOTES_ROOT)
        return 1

    total = 0
    all_problems = []

    for folder, _, files in os.walk(NOTES_ROOT):
        if ".obsidian" in folder:
            continue
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(folder, name)
            filled, problems = sync(path)
            if filled or problems:
                print("%-44s 코드 %d개" % (name, filled))
            total += filled
            all_problems.extend(problems)

    print("")
    print("채운 코드 블록 %d개" % total)

    for problem in all_problems:
        print("  문제: " + problem)

    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
