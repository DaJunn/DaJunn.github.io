#!/usr/bin/env python3
"""网页馆导航页生成器。

扫描本文件夹（含子目录）里所有 .html，自动生成本馆总目录 index.html。
以后新增页面：把 html 文件丢进本文件夹（或子文件夹），然后跑:
    python3 build_index.py
不认识的文件也能收录：标题取 <title>，说明留空显示文件名。
"""
import html
import os
import re
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "index.html")

# 说明与标签：按文件名匹配（挪位置不影响）
DESC = {
    "business_live_ecommerce.html": "三合一总入口：单位经济学 / 现金流跑道 / 增长曲线",
    "business_cashflow_runway.html": "模拟经营一家 SaaS 公司，看现金流能撑几个月",
    "business_ltv_cac.html": "LTV 与 CAC 的盈亏平衡仪表盘",
    "business_growth.html": "复利曲线与病毒系数：增长的两条曲线",
    "mcn_model.html": "直播达人 MCN 孵化机构的业务模型推演",
    "local_vs_global_optimum.html": "局部最优 vs 全局最优的交互演示",
    "人生推演台.html": "人生推演台 · 成品版（晴空仪表台方向）",
    "draft_A_晴空仪表台.html": "方向 A 草稿 · 晴空仪表台",
    "draft_B_纸上长卷.html": "方向 B 草稿 · 纸上长卷",
    "draft_C_夜航海图.html": "方向 C 草稿 · 夜航海图",
    "test_engine.html": "推演引擎的测试页",
}
GROUPS = [  # (组名, 判定函数)
    ("经营模型", lambda rel, name: "/" not in rel and (name.startswith("business_") or name == "mcn_model.html")),
    ("思维模型", lambda rel, name: "/" not in rel and name == "local_vs_global_optimum.html"),
    ("人生推演台", lambda rel, name: rel.startswith("life_sim/") and name == "人生推演台.html"),
    ("草稿与测试", lambda rel, name: rel.startswith("life_sim/") and (name.startswith("draft_") or name == "test_engine.html")),
]
FALLBACK_GROUP = "其他"
TAGS = [  # (标签, 判定函数)
    ("🔒 私藏不上线", lambda rel, name: rel.startswith("life_sim/") or name == "mcn_model.html"),
    ("草稿", lambda rel, name: name.startswith("draft_")),
    ("测试", lambda rel, name: name == "test_engine.html"),
]
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def human_size(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} MB"
    return f"{max(n // 1024, 1)} KB"


def pick(groups, rel, name):
    for label, test in groups:
        if test(rel, name):
            return label
    return None


def main():
    pages = []
    for dirpath, _dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            if not fn.lower().endswith(".html"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            if rel == "index.html":
                continue
            rel_posix = rel.replace(os.sep, "/")
            try:
                text = open(full, encoding="utf-8", errors="replace").read(200_000)
            except OSError:
                text = ""
            m = TITLE_RE.search(text)
            title = html.unescape(m.group(1)).strip() if m else fn
            stat = os.stat(full)
            group = pick(GROUPS, rel_posix, fn) or FALLBACK_GROUP
            tag = pick(TAGS, rel_posix, fn) or "成品"
            pages.append({
                "rel": rel_posix,
                "name": fn,
                "title": title,
                "desc": DESC.get(fn, ""),
                "group": group,
                "tag": tag,
                "size": human_size(stat.st_size),
                "mtime": stat.st_mtime,
                "date": time.strftime("%Y-%m-%d", time.localtime(stat.st_mtime)),
            })

    total_kb = 0
    latest = 0.0
    for p in pages:
        latest = max(latest, p["mtime"])
    summary = f"{len(pages)} 个页面 · 最近更新 {time.strftime('%Y-%m-%d', time.localtime(latest))}"

    # 组顺序按 GROUPS 定义，未知组排最后；组内按标题
    order = {g[0]: i for i, g in enumerate(GROUPS)}
    groups = {}
    for p in pages:
        groups.setdefault(p["group"], []).append(p)
    for items in groups.values():
        items.sort(key=lambda p: p["title"])

    card_tpl = """\
      <a class="card" href="{rel}" target="_blank" data-key="{key}">
        <div class="card-top"><span class="tag tag-{tagcls}">{tag}</span><span class="date">{date}</span></div>
        <h3>{title}</h3>
        <p>{desc}</p>
        <div class="meta">{name} · {size}</div>
      </a>"""

    sections = []
    for gname in sorted(groups, key=lambda g: order.get(g, 99)):
        cards = "".join(
            card_tpl.format(
                rel=html.escape(p["rel"], quote=True),
                key=html.escape((p["title"] + " " + p["desc"] + " " + p["name"]).lower(), quote=True),
                tagcls={"草稿": "draft", "测试": "test", "🔒 私藏不上线": "private"}.get(p["tag"], "final"),
                tag=p["tag"],
                date=p["date"],
                title=html.escape(p["title"]),
                desc=html.escape(p["desc"]),
                name=html.escape(p["name"]),
                size=p["size"],
            )
            for p in groups[gname]
        )
        sections.append(f"""\
    <section>
      <h2><span class="dot"></span>{html.escape(gname)}<span class="count">{len(groups[gname])}</span></h2>
      <div class="grid">
{cards}
      </div>
    </section>""")

    page = f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>我的网页馆 · 总目录</title>
<style>
  :root {{ --ink:#1a1d29; --sub:#6b7280; --line:#e5e7eb; --accent:#4f46e5; --bg:#f6f7fb; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
         background:var(--bg); color:var(--ink); padding:48px 20px 80px; }}
  .wrap {{ max-width:1080px; margin:0 auto; }}
  header h1 {{ font-size:30px; letter-spacing:.5px; }}
  header h1 em {{ font-style:normal; color:var(--accent); }}
  header .summary {{ color:var(--sub); margin-top:8px; font-size:14px; }}
  .bar {{ display:flex; gap:12px; align-items:center; margin:24px 0 8px; }}
  #q {{ flex:1; max-width:380px; padding:10px 14px; border:1px solid var(--line); border-radius:10px;
       font-size:14px; background:#fff; outline:none; }}
  #q:focus {{ border-color:var(--accent); }}
  #hit {{ color:var(--sub); font-size:13px; }}
  section {{ margin-top:36px; }}
  h2 {{ font-size:17px; display:flex; align-items:center; gap:8px; }}
  h2 .dot {{ width:8px; height:8px; border-radius:50%; background:var(--accent); display:inline-block; }}
  h2 .count {{ color:var(--sub); font-weight:400; font-size:13px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; margin-top:14px; }}
  .card {{ display:block; background:#fff; border:1px solid var(--line); border-radius:14px; padding:16px 18px;
          text-decoration:none; color:inherit; transition:.15s; }}
  .card:hover {{ border-color:var(--accent); box-shadow:0 6px 18px rgba(79,70,229,.10); transform:translateY(-2px); }}
  .card-top {{ display:flex; justify-content:space-between; align-items:center; }}
  .tag {{ font-size:11px; padding:2px 8px; border-radius:99px; }}
  .tag-final {{ background:#ecfdf5; color:#059669; }}
  .tag-draft {{ background:#fffbeb; color:#b45309; }}
  .tag-test {{ background:#f1f5f9; color:#64748b; }}
  .tag-private {{ background:#fdf2f8; color:#be185d; }}
  .date {{ color:#9ca3af; font-size:12px; }}
  .card h3 {{ font-size:15.5px; margin-top:10px; line-height:1.4; }}
  .card p {{ font-size:13px; color:var(--sub); margin-top:6px; line-height:1.55; min-height:1.55em; }}
  .meta {{ font-size:12px; color:#9ca3af; margin-top:10px; word-break:break-all; }}
  footer {{ margin-top:56px; color:var(--sub); font-size:13px; line-height:1.8; border-top:1px solid var(--line); padding-top:16px; }}
  footer code {{ background:#eef0f6; padding:1px 6px; border-radius:6px; font-size:12px; }}
  .hide {{ display:none !important; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>我的<em>网页馆</em></h1>
    <div class="summary">{summary}</div>
  </header>
  <div class="bar">
    <input id="q" type="search" placeholder="搜索页面（标题 / 说明 / 文件名）…">
    <span id="hit"></span>
  </div>
{chr(10).join(sections)}
  <footer>
    新增页面：把 <code>.html</code> 丢进本文件夹 → 跑 <code>python3 build_index.py</code> 重新生成目录 → 让 Agent 推送上线。<br>
    本页在 GitHub Pages 上就是网站首页；本地双击也能直接用。
  </footer>
</div>
<script>
  const q = document.getElementById('q'), hit = document.getElementById('hit'),
        cards = [...document.querySelectorAll('.card')], secs = [...document.querySelectorAll('section')];
  q.addEventListener('input', () => {{
    const k = q.value.trim().toLowerCase(); let n = 0;
    cards.forEach(c => {{ const on = !k || c.dataset.key.includes(k); c.classList.toggle('hide', !on); if (on) n++; }});
    secs.forEach(s => s.classList.toggle('hide', !s.querySelector('.card:not(.hide)')));
    hit.textContent = k ? `匹配 ${{n}} / ${{cards.length}}` : '';
  }});
</script>
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"已生成 {OUT}：{len(pages)} 个页面，{len(groups)} 个分组（{ '、'.join(groups) }）")


if __name__ == "__main__":
    main()
