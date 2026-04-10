# journal.py

A minimal daily journal for the terminal. Entries are stored as plain JSON — no database, no dependencies, no cloud.

Built as day 2 of [365 days of code](https://github.com/).

---

## Requirements

- Python 3.6+
- Works on Windows, macOS, Linux

## Setup

```bash
# clone or just download journal.py
python journal.py
```

No pip installs needed. Pure stdlib.

---

## Usage

```bash
python journal.py                # write today's entry
python journal.py read           # read today's entry
python journal.py read -d 5      # read last 5 entries
python journal.py list           # list all dates with word counts
python journal.py search <term>  # search across all entries
python journal.py stats          # streaks, totals, busiest day
```

## Setting your editor

The tool opens your `$EDITOR` environment variable. If it's not set, it defaults to `nano`.

**Windows:**
```bash
set EDITOR=notepad
# or for VS Code:
set EDITOR=code --wait
```

**macOS / Linux:**
```bash
export EDITOR=vim
# or
export EDITOR="code --wait"
```

To make it permanent, add the `export` line to your `~/.bashrc` or `~/.zshrc`.

---

## Storage

All entries are saved to `~/.journal.json` (your home directory). The format is straightforward:

```json
{
  "2026-04-10": {
    "created": "2026-04-10T09:00:00",
    "updated": "2026-04-10T09:15:00",
    "text": "Today I built a terminal journal...",
    "words": 312
  }
}
```

Back it up, sync it with Dropbox, commit it to a private repo — it's just a file.

---

## Commands in detail

### Write
```bash
python journal.py
```
Opens today's entry in your editor. If an entry already exists for today, it opens it for editing.

### Read
```bash
python journal.py read          # today
python journal.py read -d 3     # last 3 days
```

### List
```bash
python journal.py list
```
Shows all entry dates with a word-count bar so you can see your most productive days at a glance.

### Search
```bash
python journal.py search focus
python journal.py search "side project"
```
Searches all entries and highlights matching lines.

### Stats
```bash
python journal.py stats
```
Shows total entries, total words, average per entry, current streak, longest streak, and most active day of the week.

---

## License

MIT