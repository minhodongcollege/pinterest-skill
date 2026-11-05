# Pinterest skill for Claude Code and Codex

Lets your AI search Pinterest, read public boards, and download images as references. No Pinterest login, no API key. It only reads.

## Install (paste this into Claude Code or Codex)

> Install the Pinterest skill from https://github.com/minhodongcollege/pinterest-skill

Then just ask:

> Find 10 Pinterest references for a calm skincare brand, save them to my Desktop, and tell me what they have in common.

## For the AI doing the install
Put this repo's files in the user's skills folder as a folder named `pinterest`:
- Claude Code: `~/.claude/skills/pinterest/`
- Codex: `~/.codex/skills/pinterest/`

If `git` is available: `git clone https://github.com/minhodongcollege/pinterest-skill ~/.claude/skills/pinterest` (swap the path for Codex).
No git: download https://github.com/minhodongcollege/pinterest-skill/archive/refs/heads/main.zip, unzip it, and move the `pinterest-skill-main` folder there as `pinterest`.

Then run `python3 scripts/pin.py selftest` from that folder (`python` on Windows). It should print `ok`. Tell the user the skill is ready and may need a new chat to show up.

## Requirements
Python 3 (already on most Macs; Windows: python.org). Works on Mac and Windows.

## Note
Uses Pinterest's public website data, not the official API, so it can break if Pinterest changes its site. Be kind: small searches, not hundreds of images.

Made by [Minho Dong](https://minhodong.com).
