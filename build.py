#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build ערוץ האמונה - assemble every page from the shared shell.

Static HTML, no framework, no node. `pages/*.html` holds body fragments;
`_shell-head.html` / `_shell-foot.html` hold the header, nav and footer that
every page shares. Editing the nav in one place beats editing it in five.

The lessons page is different: it is GENERATED from `data/shiurim.json`,
because it changes weekly. Yaakov sends a link in Telegram, the agent appends
an entry, and this runs.

The `approved` flag on a lesson is the whole point of that file. A lesson by
another rabbi reaches the page ONLY once Yaakov confirms he has that rabbi's
permission, so a link can be parked safely while permission is pending.

    py build/haemuna-site/build.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = "ערוץ האמונה"

PAGES = {
    "index.html": ("home", f"{SITE} | הרב יעקב מאור",
                   "אמונה תמימה, אהבת חינם ועבודה יומיומית. שיעורים, ספרים ותוכן "
                   "על אמונה מאת הרב יעקב מאור."),
    "books.html": ("books", f"הספרים | {SITE}",
                   "כוח האמונה, לחיות תומר דבורה ורק הנשמה - מהדורות דיגיטליות "
                   "לקריאה בטלפון."),
    "about.html": ("about", f"אודות | {SITE}",
                   "הרב יעקב מאור - ראש כולל אורות האמונה בני משה, מלמד אמונה "
                   "ומחבר הספרים."),
    "shiurim.html": ("shiurim", f"שיעורים | {SITE}",
                     "שיעורי רבני הכולל ושיעורים נבחרים מרבנים אחרים, באישורם, "
                     "עם הסבר על כל שיעור."),
}


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def shell(active: str, title: str, desc: str, body: str) -> str:
    head = (HERE / "_shell-head.html").read_text(encoding="utf-8")
    foot = (HERE / "_shell-foot.html").read_text(encoding="utf-8")
    head = head.replace("{{TITLE}}", esc(title)).replace("{{DESC}}", esc(desc))
    for key in ("home", "shiurim", "books", "about"):
        head = head.replace("{{NAV_%s}}" % key.upper(),
                            ' class="active"' if key == active else "")
    return head + "\n" + body.rstrip() + "\n\n" + foot


def shiur_section(block: dict) -> str:
    items = [i for i in block.get("items", []) if i.get("approved")]
    out = ['<section>', '  <div class="wrap">',
           f'    <h2 class="section-title">{esc(block["title"])}</h2>',
           f'    <p class="section-intro">{esc(block["intro"])}</p>']
    if not items:
        out.append('    <p class="empty-note">עוד לא פורסמו כאן שיעורים. בקרוב.</p>')
    else:
        out.append('    <div class="shiurim">')
        for it in items:
            out += [
                '      <article class="shiur">',
                f'        <h3><a href="{esc(it["url"])}" target="_blank" rel="noopener">{esc(it["title"])}</a></h3>',
                f'        <p class="shiur-rav">{esc(it["rav"])}</p>',
                f'        <p class="shiur-why">{esc(it["why"])}</p>',
                f'        <a class="shiur-link" href="{esc(it["url"])}" target="_blank" rel="noopener">לשיעור</a>',
                '      </article>']
        out.append('    </div>')
    out += ['  </div>', '</section>']
    return "\n".join(out)


def shiurim_body() -> tuple:
    data = json.loads((HERE / "data" / "shiurim.json").read_text(encoding="utf-8"))
    body = "\n\n".join([
        '<div class="page-head">\n  <div class="wrap">\n'
        '    <h1>שיעורים</h1>\n'
        '    <p>שיעורים של רבני הכולל, ולצידם שיעורים של רבנים אחרים שאני לומד '
        'מהם. כל שיעור כאן עולה באישור, ולצידו הסבר קצר למה הוא נמצא כאן.</p>\n'
        '  </div>\n</div>',
        shiur_section(data["kollel"]),
        shiur_section(data["guests"]),
    ])
    live = sum(len([i for i in data[k]["items"] if i.get("approved")])
               for k in ("kollel", "guests"))
    held = sum(len([i for i in data[k]["items"] if not i.get("approved")])
               for k in ("kollel", "guests"))
    return body, live, held


def main():
    for name, (active, title, desc) in PAGES.items():
        if name == "shiurim.html":
            body, live, held = shiurim_body()
        else:
            body = (HERE / "pages" / name).read_text(encoding="utf-8")
        (HERE / name).write_text(shell(active, title, desc, body), encoding="utf-8")
        print(f"  {name}")
    print(f"נבנו {len(PAGES)} עמודים. שיעורים: {live} פורסמו, {held} ממתינים לאישור.")


if __name__ == "__main__":
    main()
