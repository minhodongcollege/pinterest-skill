---
name: pinterest
description: Search Pinterest, read public boards, and download pin images as references. Use when the user asks for Pinterest references, a mood board, inspiration images, "find pins", or pastes a pinterest.com board link. Read-only, no login or API key needed.
---

# Pinterest

Use `scripts/pin.py` in this skill's folder. It needs Python 3 and nothing else (no installs, no key).
Run it as `python3` (Mac) or `python` / `py` (Windows).

```
python3 scripts/pin.py search "QUERY" -n 10 --save DIR    # search pins, download images
python3 scripts/pin.py pins USER/BOARD -n 30 --save DIR   # a public board (USER/BOARD or the full board URL)
python3 scripts/pin.py boards USER                        # list someone's public boards
python3 scripts/pin.py selftest                           # prints "ok" if Pinterest still works with this tool
```

Output: one pin per line, tab-separated: id, title, image URL, source link. `--save` downloads the images as `<id>.jpg`.

## How to help the user
- Default to `-n 10` and save into a clear folder, e.g. `~/Desktop/pinterest-refs/<topic>` (on Windows: `%USERPROFILE%\Desktop\pinterest-refs\<topic>`). Tell them where the images are.
- After downloading, LOOK at the images and describe what they share (color, type, layout, mood). That's the useful part.
- Short, visual search words work best: "minimal skincare packaging", not long sentences.

## If something fails
- Python missing (`command not found`): tell the user to install Python 3 from python.org (Mac: or accept the "install developer tools" popup), then try again.
- Sandbox blocks the internet (Codex): ask the user to allow network access for this command.
- "Pinterest said: ..." or empty results: run `selftest`. If it fails, Pinterest changed its site and the tool needs an update.
- Secret boards need the user's own login cookie: set env `PINTEREST_COOKIE='_pinterest_sess=...'` (copied from their browser). Only offer this if they ask about secret boards.
