#!/usr/bin/env python3
"""
journal.py — daily notes from the terminal
Day 2 of 365 days of code

Usage:
  python journal.py              # write today's entry
  python journal.py read         # read today's entry
  python journal.py read -d 3    # read last 3 days
  python journal.py list         # list all entry dates
  python journal.py search <term># search across all entries
  python journal.py stats        # show writing stats
"""

import json
import os
import sys
import argparse
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

JOURNAL_FILE = Path.home() / ".journal.json"
DATE_FMT = "%Y-%m-%d"
DISPLAY_FMT = "%A, %B %-d %Y"


# ── storage ──────────────────────────────────────────────────────────────────

def load() -> dict:
    if JOURNAL_FILE.exists():
        try:
            return json.loads(JOURNAL_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def save(data: dict):
    JOURNAL_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ── colours ───────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

def c(color, text): return f"{color}{text}{RESET}"


# ── helpers ───────────────────────────────────────────────────────────────────

def today_key() -> str:
    return datetime.now().strftime(DATE_FMT)

def fmt_date(key: str) -> str:
    return datetime.strptime(key, DATE_FMT).strftime(DISPLAY_FMT)

def word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0

def open_in_editor(initial: str = "") -> str:
    editor = os.environ.get("EDITOR", "nano")
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(initial)
        fname = f.name
    subprocess.call([editor, fname])
    text = Path(fname).read_text()
    os.unlink(fname)
    return text.strip()

def divider(width=56):
    print(c(GRAY, "─" * width))

def header(title: str):
    print()
    print(c(BOLD + CYAN, f"  {title}"))
    divider()


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_write(args):
    data = load()
    key = today_key()
    existing = data.get(key, {}).get("text", "")

    if existing:
        print(c(YELLOW, f"\n  Entry exists for today ({fmt_date(key)})."))
        print(c(GRAY,   "  Opening to edit — save and close to update.\n"))
    else:
        print(c(GREEN,  f"\n  New entry — {fmt_date(key)}"))
        print(c(GRAY,   "  Opening editor. Save and close when done.\n"))

    text = open_in_editor(existing)

    if not text:
        print(c(GRAY, "\n  Nothing saved (empty entry).\n"))
        return

    now = datetime.now().isoformat(timespec="seconds")
    if key not in data:
        data[key] = {"created": now}
    data[key]["text"] = text
    data[key]["updated"] = now
    data[key]["words"] = word_count(text)
    save(data)

    wc = data[key]["words"]
    print(c(GREEN, f"\n  Saved. ") + c(GRAY, f"{wc} word{'s' if wc!=1 else ''}.") + "\n")


def cmd_read(args):
    data = load()
    days = getattr(args, "days", 1)
    keys = sorted(data.keys(), reverse=True)[:days]

    if not keys:
        print(c(GRAY, "\n  No entries yet. Run without arguments to write your first.\n"))
        return

    for key in reversed(keys):
        entry = data[key]
        header(fmt_date(key))
        text = entry.get("text", "")
        for line in text.splitlines():
            print(f"  {line}")
        wc = entry.get("words", word_count(text))
        print()
        print(c(GRAY, f"  {wc} words · updated {entry.get('updated', '?')[:10]}"))
        divider()
    print()


def cmd_list(args):
    data = load()
    if not data:
        print(c(GRAY, "\n  No entries yet.\n"))
        return

    header("all entries")
    keys = sorted(data.keys())
    streak, cur = 0, 0
    prev = None
    for k in keys:
        d = datetime.strptime(k, DATE_FMT)
        if prev and (d - prev).days == 1:
            cur += 1
            streak = max(streak, cur)
        else:
            cur = 1
        prev = d

    for key in reversed(keys):
        wc = data[key].get("words", 0)
        bar = "█" * min(wc // 20, 20)
        is_today = key == today_key()
        marker = c(GREEN, " ← today") if is_today else ""
        print(f"  {c(CYAN, key)}  {c(GRAY, f'{wc:>5} words')}  {c(GREEN, bar)}{marker}")
    print()
    total_words = sum(e.get("words", 0) for e in data.values())
    print(c(GRAY, f"  {len(keys)} entries · {total_words} words total · longest streak {streak} days"))
    print()


def cmd_search(args):
    data = load()
    term = " ".join(args.term).lower()
    if not term:
        print(c(GRAY, "\n  Usage: journal.py search <term>\n"))
        return

    header(f'search: "{term}"')
    found = 0
    for key in sorted(data.keys(), reverse=True):
        text = data[key].get("text", "")
        if term in text.lower():
            found += 1
            print(c(CYAN, f"  {key}  ") + c(GRAY, fmt_date(key)))
            for line in text.splitlines():
                if term in line.lower():
                    idx = line.lower().index(term)
                    hi = line[:idx] + c(YELLOW + BOLD, line[idx:idx+len(term)]) + line[idx+len(term):]
                    print(f"    {c(GRAY, '›')} {hi}")
            print()
    if not found:
        print(c(GRAY, f"  No entries containing \"{term}\".\n"))
    else:
        print(c(GRAY, f"  {found} entr{'y' if found==1 else 'ies'} matched.\n"))


def cmd_stats(args):
    data = load()
    if not data:
        print(c(GRAY, "\n  No entries yet.\n"))
        return

    header("stats")
    keys = sorted(data.keys())
    total = len(keys)
    total_words = sum(e.get("words", 0) for e in data.values())
    avg = total_words // total if total else 0

    # streak calc
    streak, cur, best_streak = 0, 0, 0
    prev = None
    for k in keys:
        d = datetime.strptime(k, DATE_FMT)
        if prev and (d - prev).days == 1:
            cur += 1
        else:
            cur = 1
        best_streak = max(best_streak, cur)
        prev = d

    # current streak
    check = datetime.now()
    cur_streak = 0
    while True:
        if check.strftime(DATE_FMT) in data:
            cur_streak += 1
            check -= timedelta(days=1)
        else:
            break

    # busiest day of week
    from collections import Counter
    dow = Counter(datetime.strptime(k, DATE_FMT).strftime("%A") for k in keys)
    busiest = dow.most_common(1)[0][0] if dow else "—"

    print(f"  {c(WHITE, 'Entries')}         {c(GREEN, total)}")
    print(f"  {c(WHITE, 'Total words')}      {c(GREEN, total_words)}")
    print(f"  {c(WHITE, 'Avg per entry')}    {c(GREEN, avg)} words")
    print(f"  {c(WHITE, 'Current streak')}   {c(GREEN, cur_streak)} day{'s' if cur_streak!=1 else ''}")
    print(f"  {c(WHITE, 'Longest streak')}   {c(GREEN, best_streak)} day{'s' if best_streak!=1 else ''}")
    print(f"  {c(WHITE, 'Most active day')}  {c(GREEN, busiest)}")
    print(f"  {c(WHITE, 'First entry')}      {c(CYAN, keys[0])}")
    print(f"  {c(WHITE, 'Latest entry')}     {c(CYAN, keys[-1])}")
    print(f"  {c(WHITE, 'Stored at')}        {c(GRAY, str(JOURNAL_FILE))}")
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="journal",
        description="daily notes from the terminal",
        add_help=True
    )
    sub = parser.add_subparsers(dest="cmd")

    p_read = sub.add_parser("read", help="read entries")
    p_read.add_argument("-d", "--days", type=int, default=1, metavar="N",
                        help="number of recent entries to show (default: 1)")

    sub.add_parser("list", help="list all entry dates")

    p_search = sub.add_parser("search", help="search entries")
    p_search.add_argument("term", nargs="+", help="search term")

    sub.add_parser("stats", help="writing stats")

    args = parser.parse_args()

    if args.cmd == "read":    cmd_read(args)
    elif args.cmd == "list":  cmd_list(args)
    elif args.cmd == "search":cmd_search(args)
    elif args.cmd == "stats": cmd_stats(args)
    else:                     cmd_write(args)


if __name__ == "__main__":
    main()
