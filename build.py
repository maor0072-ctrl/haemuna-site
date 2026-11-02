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
NL = chr(10)
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
    "rosh-hashana.html": ("rosh", f"רעיונות לקבלות לראש השנה | {SITE}",
                          "רעיונות לקבלות לימים הנוראים - 139 קבלות מעשיות "
                          "לפי נושאים, לגברים ולנשים, ואיך בוחרים קבלה שאפשר "
                          "לעמוד בה."),
    "ma-over-alecha.html": ("matzav", f"מה עובר עליך | {SITE}",
                            "מילה למי שנמצא עכשיו בתוך הקושי - פרנסה, אבל, פחד - "
                            "מאת הרב יעקב מאור."),
    "parnasa.html": ("matzav", f"כשהפרנסה לוחצת | {SITE}",
                     "חובות, פיטורים, עסק שמתפרק: על השתדלות בלי בהלה, למי שייך "
                     "הכסף, ומה אפשר לעשות כבר היום."),
    "mehashiur.html": ("shiurim", f"מתוך השיעור השבועי | {SITE}",
                       "רעיונות, סיפורים ותשובות מתוך השיעור השבועי של הרב יעקב "
                       "מאור, לפי נושאים: אמונה, מידות ועוד."),
    "harav.html": ("shiurim", f"שיעורים של הרב יעקב מאור | {SITE}",
                   "שיעורי וידאו מלאים של הרב יעקב מאור מהשיעור השבועי בכולל, "
                   "עם כתוביות, לצפייה בטלפון ובמחשב."),
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
    for key in ("home", "rosh", "matzav", "shiurim", "books", "about"):
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


# התוכן יושב באתר המקדש ("המקדש הוא התוכן, השני הוא הקישור", הכרעה ג6) - כאן רק קישורים
MIKDASH_LIBRARY = """<section>
  <div class="wrap prose">
    <h2 class="section-title">ספריית השיעורים</h2>
    <p>יותר מאלף שיעורים וסרטונים שלי, לצפייה ישירה, יושבים באתר העמותה: <a href="https://hamikdash.co.il/videos/">לספריית השיעורים והסרטונים</a>.</p>
    <h3>מאמרים לפי נושא</h3>
    <ul>
      <li><a href="https://hamikdash.co.il/torah/bitachon-vehishtadlut.html">ביטחון והשתדלות</a> - לפרנסה, ללחץ ולדאגה</li>
      <li><a href="https://hamikdash.co.il/torah/tefila-shelo-nenata.html">תפילה שלא נענתה</a> - למי שמתפלל שנים ולא רואה תשובה</li>
      <li><a href="https://hamikdash.co.il/torah/chinuch-yeladim.html">חינוך ילדים</a> - להורים</li>
      <li><a href="https://hamikdash.co.il/torah/zugiyut-vekaas.html">זוגיות וכעס</a> - לבית ולזוגיות</li>
      <li><a href="https://hamikdash.co.il/torah/ahavat-chinam.html">אהבת חינם</a> - למחלוקת ולפגיעה</li>
      <li><a href="https://hamikdash.co.il/torah/shabbat-vebayit.html">שבת ובית</a> - לבית ולילדים</li>
    </ul>
    <p><a href="https://hamikdash.co.il/chagim/">חגים ומועדים</a> - ראש השנה, יום כיפור, סוכות, פסח והצומות.</p>
  </div>
</section>"""


# קטעים מהשיעור השבועי: רק מה שיעקב אישר בסבב היומי (scripts/shiur_daily_review.py).
# הבנק של ה-AIOS הוא מקור האמת; כאן נשמר עותק, כי הריפו של האתר עומד בפני עצמו.
BANK = HERE.parent.parent / "outputs" / "content" / "post-bank" / "shiur-shvui" / "index.json"
BANK_COPY = HERE / "data" / "mehashiur.json"
CAT_ORDER = ["אמונה", "מידות", "תפילה", "השגחה", "בין אדם לחברו", "בית וזוגיות", "חינוך"]


def bank_items() -> list:
    if BANK.exists():
        BANK_COPY.write_text(BANK.read_text(encoding="utf-8"), encoding="utf-8")
    return json.loads(BANK_COPY.read_text(encoding="utf-8")) if BANK_COPY.exists() else []


def source_line(it: dict) -> str:
    s = str(it.get("source", ""))
    line = ("מקור: " + s.split(":", 1)[-1].strip()) if s.startswith("other") else "מתוך השיעור השבועי"
    return line + (f" · מפגש {it['meeting']}" if it.get("meeting") else "")


def mehashiur_body() -> str:
    items = bank_items()
    by = {}
    for it in items:
        by.setdefault(it["cat"], []).append(it)
    cats = sorted(by, key=lambda c: (CAT_ORDER.index(c) if c in CAT_ORDER else 99, c))
    toc = " · ".join(f'<a href="#{esc(c)}">{esc(c)}</a>' for c in cats)
    head = ['<div class="page-head">', '  <div class="wrap">',
            '    <h1>מתוך השיעור השבועי</h1>',
            '    <p>רעיונות, סיפורים ותשובות לשאלות שעלו בשיעור השבועי, לפי נושאים. '
            'כל קטע נבדק מול המקור לפני שעלה לכאן.</p>']
    if toc:
        head.append(f'    <p>{toc}</p>')
    head += ['  </div>', '</div>']
    out = [NL.join(head)]
    if not items:
        out.append('<section><div class="wrap"><p class="empty-note">בקרוב.</p></div></section>')
    for c in cats:
        sec = ['<section>', '  <div class="wrap prose">',
               f'    <h2 class="section-title" id="{esc(c)}">{esc(c)}</h2>']
        for it in by[c]:
            sec.append('    <article class="shiur">')
            sec.append(f'      <h3>{esc(it.get("hook") or it.get("title"))}</h3>')
            sec += [f'      <p>{esc(par)}</p>' for par in str(it["body"]).split(NL) if par.strip()]
            sec.append(f'      <p class="shiur-rav">{esc(source_line(it))}</p>')
            sec.append('    </article>')
        sec += ['  </div>', '</section>']
        out.append(NL.join(sec))
    return (NL + NL).join(out)


LINK_MEHASHIUR = NL.join([
    '<section>', '  <div class="wrap prose">',
    '    <h2 class="section-title">מתוך השיעור השבועי</h2>',
    '    <p>רעיונות, סיפורים ותשובות מהשיעור השבועי, לפי נושאים: '
    '<a href="/mehashiur.html">לקטעים מהשיעור</a>.</p>',
    '  </div>', '</section>'])


# שיעורי הווידאו של הרב: data/shiurim.json, המפתח "harav". הווידאו יושב ביוטיוב
# (לא רשום, המפתח "youtube") או בדרייב (המפתח "drive"), והעמוד מטמיע אותו.
# החדש ביותר למעלה.
def embed_src(it: dict) -> str:
    if it.get("youtube"):
        return f"https://www.youtube-nocookie.com/embed/{it['youtube']}?rel=0"
    return f"https://drive.google.com/file/d/{it['drive']}/preview"

def harav_body() -> str:
    data = json.loads((HERE / "data" / "shiurim.json").read_text(encoding="utf-8"))
    block = data.get("harav", {})
    items = sorted([i for i in block.get("items", []) if i.get("approved")],
                   key=lambda i: i.get("added", ""), reverse=True)
    out = ['<div class="page-head">', '  <div class="wrap">',
           '    <h1>שיעורים של הרב יעקב מאור</h1>',
           f'    <p>{esc(block.get("intro", ""))}</p>', '  </div>', '</div>',
           '<section>', '  <div class="wrap prose">']
    if not items:
        out.append('    <p class="empty-note">עוד לא עלו כאן שיעורים. בקרוב.</p>')
    for it in items:
        out += ['    <article class="shiur shiur-video">',
                f'      <h2>{esc(it["title"])}</h2>',
                f'      <p class="shiur-rav">{esc(it["when"])}</p>',
                '      <div class="video-frame">',
                f'        <iframe src="{esc(embed_src(it))}" '
                f'title="{esc(it["title"])}" loading="lazy" allow="accelerometer; encrypted-media; '
                'gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe>',
                '      </div>']
        out += [f'      <p>{esc(par)}</p>' for par in str(it["about"]).split(NL) if par.strip()]
        out.append('    </article>')
    out += ['  </div>', '</section>']
    return NL.join(out)


LINK_HARAV = NL.join([
    '<section>', '  <div class="wrap prose">',
    '    <h2 class="section-title">שיעורים של הרב יעקב מאור</h2>',
    '    <p>שיעורי וידאו מלאים מהשיעור השבועי בכולל, עם כתוביות: '
    '<a href="/harav.html">לתיקיית השיעורים של הרב</a>.</p>',
    '  </div>', '</section>'])


def shiurim_body() -> tuple:
    data = json.loads((HERE / "data" / "shiurim.json").read_text(encoding="utf-8"))
    body = "\n\n".join([
        '<div class="page-head">\n  <div class="wrap">\n'
        '    <h1>שיעורים</h1>\n'
        '    <p>שיעורים של רבני הכולל, ולצידם שיעורים של רבנים אחרים שאני לומד '
        'מהם. כל שיעור כאן עולה באישור, ולצידו הסבר קצר למה הוא נמצא כאן.</p>\n'
        '  </div>\n</div>',
        LINK_HARAV,
        LINK_MEHASHIUR,
        MIKDASH_LIBRARY,
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
        elif name == "harav.html":
            body = harav_body()
        elif name == "mehashiur.html":
            body = mehashiur_body()
        else:
            body = (HERE / "pages" / name).read_text(encoding="utf-8")
        (HERE / name).write_text(shell(active, title, desc, body), encoding="utf-8")
        print(f"  {name}")
    print(f"נבנו {len(PAGES)} עמודים. שיעורים: {live} פורסמו, {held} ממתינים לאישור.")


if __name__ == "__main__":
    main()
