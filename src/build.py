"""mktoho.dev を組み立てる

使い方（リポジトリの一番上で）:
    uv run --with budoux --with markdown python src/build.py

- src/site.toml からトップページ index.html を作る
- src/notes/*.md から notes/<名前>/index.html を作る
- 文章は句点ごとに改行し（句点は消す）、文の中は BudouX で文節の切れ目にだけ <wbr> を入れる
"""
from __future__ import annotations

import html
import re
import tomllib
from pathlib import Path

import budoux
import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PARSER = budoux.load_default_japanese_parser()

# 英数字のあいだのハイフンでは折り返さない（rain-alert が rain- / alert に割れないように）
NBHY = "‑"


def phrase(text: str) -> str:
    """1行ぶんの文を、文節の切れ目でだけ折り返せる HTML にする"""
    text = re.sub(r"(?<=[A-Za-z0-9])-(?=[A-Za-z0-9])", NBHY, text)
    return "<wbr>".join(html.escape(c) for c in PARSER.parse(text))


def t(text: str) -> str:
    """句点で改行し、句点そのものは消す"""
    lines = [s.strip() for s in text.split("。") if s.strip()]
    return "<br>".join(phrase(s) for s in lines)


def attr(s: str) -> str:
    return html.escape(s, quote=True)


def link(url: str, inner: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{attr(url)}">{inner}</a>' if url else f"<span{c}>{inner}</span>"


FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&display=swap" rel="stylesheet">'
)


def head(title: str, desc: str, url: str, depth: str) -> str:
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{attr(desc)}">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{attr(url)}">
<meta property="og:image" content="https://mktoho.dev/og.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:site" content="@mktoho12">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="{depth}assets/site.css">
</head>
<body>
"""


FOOT = """<footer class="ft wrap">
<p>© mktoho<br>このサイトは Claude と一緒に作りました</p>
</footer>
</body>
</html>
"""

RECENT_SHOWN = 8


def build_index(site: dict) -> str:
    i = site["intro"]
    o: list[str] = []
    o.append(head(i["name"], "AIに小さなシステムを作ってもらって、シェアハウスで運用しています。いまやっていることと、興味があること、作ったもの。", "https://mktoho.dev/", "/"))

    # 冒頭
    o.append('<header class="hd"><div class="wrap hd-in">')
    o.append(f'<p class="nm"><img src="/assets/icon.png" alt="" width="40" height="40">{html.escape(i["name"])}</p>')
    o.append(f'<h1 class="lede">{t(i["lede"])}</h1>')
    o.append(f'<p class="desc">{t(i["desc"])}</p>')
    links = "".join(f'<a href="{attr(l["url"])}">{l["label"]} <span>{html.escape(l["id"])}</span></a>' for l in site["links"])
    o.append(f'<p class="links">{links}<span class="mail">{html.escape(site["contact"]["mail"])}</span></p>')
    o.append("</div></header>")
    o.append('<main class="wrap">')

    # 最近のこと
    def recent_li(r: dict) -> str:
        return f'<li><time>{html.escape(r["date"])}</time>{link(r.get("url", ""), t(r["text"]))}</li>'

    rec = site["recent"]
    o.append('<section class="recent" aria-labelledby="h-recent"><h2 id="h-recent">最近のこと</h2><ul>')
    o.extend(recent_li(r) for r in rec[:RECENT_SHOWN])
    o.append("</ul>")
    if len(rec) > RECENT_SHOWN:
        o.append('<details><summary>それより前</summary><ul>')
        o.extend(recent_li(r) for r in rec[RECENT_SHOWN:])
        o.append("</ul></details>")
    o.append("</section>")

    # 興味があること
    o.append('<section class="intr" aria-labelledby="h-intr"><h2 id="h-intr">興味があること</h2>')
    o.append(f'<p class="sub">{t(site["interests_head"]["sub"])}</p>')
    for it in site["interests"]:
        note = it.get("note")
        o.append(f'<article class="item{" has-note" if note else ""}"><h3>{html.escape(it["name"])}</h3><dl>')
        for key, label in (("now", "いま"), ("want", "知りたい"), ("enough", "間に合っている")):
            if it.get(key):
                o.append(f"<div><dt>{label}</dt><dd>{t(it[key])}</dd></div>")
        o.append("</dl>")
        if note:
            o.append(f'<figure class="note"><img src="/{attr(note)}" alt="{attr(it["name"])}について書いたノート" loading="lazy"></figure>')
        o.append("</article>")
    sns = " / ".join(f'<a href="{attr(l["url"])}">{l["label"]} {html.escape(l["id"])}</a>' for l in site["links"] if l["label"] != "GitHub")
    o.append(f'<div class="contact"><p class="lbl">連絡先</p><p>メール {html.escape(site["contact"]["mail"])} / {sns}</p></div>')
    o.append("</section>")

    # 作ったもの
    o.append('<section class="made" aria-labelledby="h-made"><h2 id="h-made">作ったもの</h2>')
    for g in site["made"]:
        o.append(f'<h3 class="grp">{html.escape(g["group"])}</h3><ul>')
        for m in g["items"]:
            o.append(f'<li>{link(m["url"], t(m["name"]), "what")}<span class="how">{t(m["how"])}</span></li>')
        o.append("</ul>")
    o.append("</section>")

    o.append("</main>")
    o.append(FOOT)
    return "\n".join(o)


def md_line(line: str) -> str:
    """Markdown の1行に、コード以外の部分だけ <wbr> を入れる"""
    parts = re.split(r"(`[^`]*`)", line)
    out = []
    for p in parts:
        if p.startswith("`"):
            out.append(p)
            continue
        m = re.match(r"^(\s*(?:#{1,6} |[-*] |\d+\. )?)(.*)$", p) if not out else None
        prefix, body = (m.group(1), m.group(2)) if m else ("", p)
        # Markdown の記号（* _ [ ] など）はほぼ使わないので、そのまま BudouX に通す
        out.append(prefix + "<wbr>".join(PARSER.parse(body.replace("。", ""))) if body else prefix)
    return "".join(out)


def build_note(path: Path) -> tuple[str, str]:
    src = path.read_text(encoding="utf-8").splitlines()
    title = src[0].removeprefix("# ").strip()
    lead = next((l for l in src[1:] if l.strip()), "")
    body, in_code = [], False
    for line in src[1:]:
        if line.startswith("```"):
            in_code = not in_code
            body.append(line)
        elif in_code or not line.strip():
            body.append(line)
        else:
            body.append(md_line(line))
    content = markdown.markdown("\n".join(body), extensions=["fenced_code", "nl2br"])
    slug = path.stem
    o = [head(f"{title} | mktoho", lead, f"https://mktoho.dev/notes/{slug}/", "../../")]
    o.append('<header class="hd hd-note"><div class="wrap hd-in">')
    o.append('<p class="nm"><a href="/"><img src="/assets/icon.png" alt="" width="40" height="40">mktoho</a></p>')
    o.append(f'<h1 class="lede">{"<wbr>".join(html.escape(c) for c in PARSER.parse(title))}</h1>')
    o.append('</div></header><main class="wrap prose">')
    o.append(content)
    o.append('<p class="back"><a href="/">トップに戻る</a></p></main>')
    o.append(FOOT)
    return slug, "\n".join(o)


def main() -> None:
    site = tomllib.loads((SRC / "site.toml").read_text(encoding="utf-8"))
    (ROOT / "index.html").write_text(build_index(site), encoding="utf-8")
    print("index.html")
    for md in sorted((SRC / "notes").glob("*.md")):
        slug, page = build_note(md)
        out = ROOT / "notes" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
