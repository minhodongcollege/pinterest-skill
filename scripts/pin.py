#!/usr/bin/env python3
"""Pinterest CLI: read public boards, pins and search; download images.

  python3 pin.py boards USER                    list a user's boards
  python3 pin.py pins USER/BOARD [-n 50] [--save DIR]   pins on a board (or paste the board URL)
  python3 pin.py search "QUERY" [-n 25] [--save DIR]    search pins
  python3 pin.py selftest

Uses Pinterest's own web endpoints, no API key. Read-only.
Secret boards: export PINTEREST_COOKIE='_pinterest_sess=...' (copied from your browser).
"""
import argparse, json, os, ssl, sys, urllib.parse, urllib.request

CTX = ssl.create_default_context()
if os.path.exists("/etc/ssl/cert.pem"):  # macOS python.org Python ships without certs
    CTX.load_verify_locations("/etc/ssl/cert.pem")
for _s in (sys.stdout, sys.stderr):  # Windows consoles choke on emoji in pin titles
    _s.reconfigure(encoding="utf-8", errors="replace")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "application/json",
    "X-Pinterest-PWS-Handler": "www/[username].js",
}
if os.environ.get("PINTEREST_COOKIE"):
    HEADERS["Cookie"] = os.environ["PINTEREST_COOKIE"]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30, context=CTX)


def resource(name, options):
    q = urllib.parse.urlencode({"source_url": "/", "data": json.dumps({"options": options, "context": {}})})
    r = json.load(get(f"https://www.pinterest.com/resource/{name}/get/?{q}"))["resource_response"]
    if r.get("status") != "success":
        sys.exit(f"Pinterest said: {r.get('message') or r}")
    return r


def paged(name, options, n, unwrap=lambda d: d):
    """Yield up to n items, following Pinterest's bookmark cursor."""
    bookmark, got = None, 0
    while got < n:
        opts = dict(options, page_size=min(n - got, 50))  # ponytail: 50/page is what the web app uses
        if bookmark:
            opts["bookmarks"] = [bookmark]
        r = resource(name, opts)
        for item in unwrap(r["data"]):
            if item.get("type", "pin") in ("pin", "board") and got < n:
                got += 1
                yield item
        bookmark = r.get("bookmark")
        if not bookmark or bookmark == "-end-" or not unwrap(r["data"]):
            return


def board_ref(s):
    """'user/board', '/user/board/' or a full board URL -> ('user', 'board')."""
    path = urllib.parse.urlparse(s).path if "://" in s else s
    parts = [p for p in path.split("/") if p]
    if len(parts) != 2:
        sys.exit(f"Can't read board '{s}'. Use USER/BOARD or the board URL.")
    return parts[0], parts[1]


def image(pin):
    imgs = pin.get("images") or {}
    return (imgs.get("orig") or imgs.get("736x") or {}).get("url", "")


def show_pins(pins, save):
    if save:
        os.makedirs(save, exist_ok=True)
    for p in pins:
        url = image(p)
        title = (p.get("title") or p.get("grid_title") or p.get("description") or "").strip().replace("\n", " ")[:60]
        print(f"{p['id']}\t{title}\t{url}\t{p.get('link') or ''}")
        if save and url:
            path = os.path.join(save, p["id"] + os.path.splitext(urllib.parse.urlparse(url).path)[1])
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.write(get(url).read())
    if save:
        print(f"# saved to {os.path.abspath(save)}", file=sys.stderr)


def cmd_boards(a):
    for b in paged("BoardsResource", {"username": a.user, "privacy_filter": "all", "field_set_key": "profile_grid_item"}, a.n):
        print(f"{b['id']}\t{b['name']}\t{b.get('pin_count', '')} pins\thttps://www.pinterest.com{b.get('url', '')}")


def cmd_pins(a):
    user, slug = board_ref(a.board)
    board = resource("BoardResource", {"username": user, "slug": slug, "field_set_key": "detailed"})["data"]
    print(f"# {board['name']} ({board.get('pin_count', '?')} pins)", file=sys.stderr)
    show_pins(paged("BoardFeedResource", {"board_id": board["id"], "board_url": board["url"], "field_set_key": "react_grid_pin"}, a.n), a.save)


def cmd_search(a):
    show_pins(paged("BaseSearchResource", {"query": a.query, "scope": "pins"}, a.n,
                    unwrap=lambda d: d.get("results", []) if isinstance(d, dict) else d), a.save)


def cmd_selftest(a):
    assert board_ref("minho/portfolio-refs") == ("minho", "portfolio-refs")
    assert board_ref("https://www.pinterest.com/minho/portfolio-refs/") == ("minho", "portfolio-refs")
    assert board_ref("/minho/portfolio-refs/") == ("minho", "portfolio-refs")
    boards = list(paged("BoardsResource", {"username": "pinterest", "privacy_filter": "all", "field_set_key": "profile_grid_item"}, 60))
    assert len(boards) == 60, f"pagination broke: got {len(boards)}"  # forces 2 pages
    assert all(image(p).startswith("https://") for p in paged("BaseSearchResource", {"query": "poster design", "scope": "pins"}, 3,
                                                               unwrap=lambda d: d.get("results", [])))
    print("ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(required=True)
    p = sub.add_parser("boards"); p.add_argument("user"); p.add_argument("-n", type=int, default=100); p.set_defaults(fn=cmd_boards)
    p = sub.add_parser("pins"); p.add_argument("board"); p.add_argument("-n", type=int, default=50); p.add_argument("--save"); p.set_defaults(fn=cmd_pins)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("-n", type=int, default=25); p.add_argument("--save"); p.set_defaults(fn=cmd_search)
    p = sub.add_parser("selftest"); p.set_defaults(fn=cmd_selftest)
    a = ap.parse_args()
    a.fn(a)
