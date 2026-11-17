r"""The catalogue page: one card per row of results.json (id, title, verdict, today's and the new picture side by side,
element counts per part, paths), pictures embedded as data URIs.

Run alone: pixi run -e addon python experiments/refinement_catalogue/make_page.py
Output: C:\Users\hamed\Desktop\delme\refinement_studies\catalogue.html"""

import base64
import html
import json
import os
import sys

RESULTS = r"C:\Users\hamed\Desktop\delme\refinement_studies\results.json"

STYLE = """
:root { --bg: #f7f7f5; --card: #ffffff; --text: #1f2328; --muted: #656d76; --line: #d8dee4; --ok: #1a7f37;
  --bad: #cf222e; --chip: #eef1f4; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #16181c; --card: #1f2227;
  --text: #e6e8eb; --muted: #9aa3ad; --line: #30363d; --ok: #3fb950; --bad: #f85149; --chip: #2a2f36; } }
:root[data-theme="dark"] { --bg: #16181c; --card: #1f2227; --text: #e6e8eb; --muted: #9aa3ad; --line: #30363d;
  --ok: #3fb950; --bad: #f85149; --chip: #2a2f36; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.45 system-ui, sans-serif; }
main { max-width: 1240px; margin: 0 auto; padding: 24px 16px 48px; }
h1 { font-size: 22px; margin: 0 0 4px; }
.lead { color: var(--muted); margin: 0 0 24px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 16px; margin: 0 0 20px; }
.head { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: baseline; }
.id { font-weight: 700; font-size: 17px; }
.verdict { padding: 1px 8px; border-radius: 99px; font-size: 13px; background: var(--chip); }
.ok { color: var(--ok); } .bad { color: var(--bad); }
.pics { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin: 12px 0; }
figure { margin: 0; } figure img { width: 100%; height: auto; border: 1px solid var(--line); border-radius: 6px;
  background: #fff; }
figcaption { color: var(--muted); font-size: 13px; margin-top: 4px; }
table { border-collapse: collapse; font-size: 13px; margin: 8px 0; }
td, th { border-bottom: 1px solid var(--line); padding: 3px 12px 3px 0; text-align: right; }
td:first-child, th:first-child { text-align: left; }
.paths { color: var(--muted); font-size: 12px; overflow-wrap: anywhere; }
.check { font-size: 13px; }
"""


def picture(path):
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def card(r):
    e = html.escape
    ok = "ok" if r["match"] else "bad"
    out = [f'<section class="card"><div class="head"><span class="id">{e(r["id"])}</span><span>{e(r["title"])}</span>']
    out.append(f'<span class="verdict {ok}">{"matches" if r["match"] else "does not match"}</span></div>')
    out.append(
        f"<p>Verdict: {e(r['verdict'])}" + ("" if r["expected"] == "meshes" else f" (expected: {e(r['expected'])})")
    )
    out.append("</p>")
    if r.get("check"):
        c = r["check"]
        out.append(f'<p class="check {"ok" if c["passed"] else "bad"}">Check: {e(c["text"])}</p>')
    pics = [(side, r.get(side, {})) for side in ("today", "new")]
    if any(p.get("png") for _, p in pics):
        out.append('<div class="pics">')
        for side, p in pics:
            caption = "today (no Refine Near)" if side == "today" else "new (with Refine Near)"
            out.append(f'<figure><img alt="{side} mesh of {e(r["id"])}" src="{picture(p.get("png"))}">')
            out.append(f"<figcaption>{caption}, {p.get('seconds', '?')} s</figcaption></figure>")
        out.append("</div>")
    if any(p.get("png_across") for _, p in pics):
        out.append('<div class="pics">')
        for side, p in pics:
            out.append(f'<figure><img alt="{side} mesh of {e(r["id"])} across" src="{picture(p.get("png_across"))}">')
            out.append(f"<figcaption>{side}, cut across</figcaption></figure>")
        out.append("</div>")
    parts = sorted(set(r.get("today", {}).get("elements", {})) | set(r.get("new", {}).get("elements", {})))
    if parts:
        out.append("<table><tr><th>part</th><th>today</th><th>new</th></tr>")
        for part in parts + ["total"]:
            vals = []
            for side in ("today", "new"):
                el = r.get(side, {}).get("elements", {})
                vals.append(sum(el.values()) if part == "total" else el.get(part, ""))
            out.append(f"<tr><td>{e(part)}</td><td>{vals[0]}</td><td>{vals[1]}</td></tr>")
        out.append("</table>")
    files = r.get("files") or {}
    out.append('<div class="paths">' + "<br>".join(f"{e(k)}: {e(str(v))}" for k, v in files.items() if v) + "</div>")
    out.append("</section>")
    return "".join(out)


def write(results=RESULTS):
    with open(results, encoding="utf-8") as fh:
        rows = json.load(fh)
    matched = sum(r["match"] for r in rows)
    body = "".join(card(r) for r in rows)
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Refinement catalogue</title>'
        f"<style>{STYLE}</style></head><body><main><h1>Refinement catalogue, Stages 1 and 2: Refine Near</h1>"
        f'<p class="lead">{matched} of {len(rows)} rows match. Each row is meshed today (its Refine Near items deleted)'
        " and new (with them); 3D pictures show the elements that cross a cut plane.</p>"
        f"{body}</main></body></html>"
    )
    path = os.path.join(os.path.dirname(results), "catalogue.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return path


if __name__ == "__main__":
    print(write(*sys.argv[1:]))
