#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内热门书单追踪器 v2
- 抓取当当网周榜 / 豆瓣新书 / 微信读书热搜
- 清理书名（去除促销文案）
- 生成带 Z-Library 搜索链接的 HTML 报告
用法: python booklist_tracker.py
"""

import requests
import json
import re
import os
import sys
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_HTML = os.path.join(OUTPUT_DIR, "hot_booklist.html")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "books.json")
ZLIB_BASE = "https://z-library.sk/s/"
MAX_BOOKS = 50

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.baidu.com/",
}


# ──────────────────────────────────────────────
# 分类推断
# ──────────────────────────────────────────────
def infer_category(title: str) -> str:
    """根据书名简单推断分类"""
    t = title.lower()
    tech_kw = ["python", "javascript", "js", "java", "编程", "程序", "算法",
                "c++", "c#", "前端", "后端", "数据库", "linux", "ai", "人工智能", "机器"]
    if any(k in t for k in tech_kw):
        return "技术"
    psy_kw = ["心理", "自卑", "勇气", "认知", "情绪", "焦虑", "抑郁", "疗愈"]
    if any(k in t for k in psy_kw):
        return "心理"
    biz_kw = ["经济", "金融", "商业", "管理", "投资", "理财", "创业", "营销", "资本"]
    if any(k in t for k in biz_kw):
        return "经管"
    grow_kw = ["成长", "高效", "自律", "习惯", "成功", "方法论", "思考", "逻辑"]
    if any(k in t for k in grow_kw):
        return "成长"
    hist_kw = ["历史", "王朝", "帝国", "战争", "古代", "近代", "世纪"]
    if any(k in t for k in hist_kw):
        return "历史"
    return "文学"


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────
def zlib_link(title: str) -> str:
    return ZLIB_BASE + quote(clean_title(title), safe="")


def is_chinese_title(title: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', title))


def clean_title(title: str) -> str:
    """去除书名中的促销描述，只保留核心书名"""
    # 常见分隔符后面的都是促销文案
    for sep in [" 当当", " 作者", "（", "【", " 精装", " 全套", " 套装",
                " 全4册", " 全3册", " 全2册", " 全5册", " 全6册",
                "（全", "（套", " 新华", " 正版", "限量", " 漓江",
                " 印签", "寄语", " 藏书票"]:
        idx = title.find(sep)
        if idx > 2:
            title = title[:idx]
    # 去除括号里的描述（保留书名部分）
    title = re.sub(r'[\(（][^)）]{5,}[\)）]', '', title)
    return title.strip()


def fetch(url: str, timeout: int = 15, extra_headers: dict = None) -> str | None:
    try:
        h = {**HEADERS, **(extra_headers or {})}
        resp = requests.get(url, headers=h, timeout=timeout)
        resp.encoding = resp.apparent_encoding or "utf-8"
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"  ⚠ HTTP {resp.status_code}: {url}")
    except Exception as e:
        print(f"  ⚠ 抓取失败: {url}  ({e})")
    return None


# ──────────────────────────────────────────────
# 数据源 1：当当网近7日畅销榜
# ──────────────────────────────────────────────
def fetch_dangdang() -> list[dict]:
    url = "http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-recent7-0-0-1-1"
    print("📚 [1/4] 当当网近7日畅销榜...")
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    items = []
    for li in soup.select("ul.bang_list li"):
        name_tag = li.select_one(".name a")
        author_tag = li.select_one(".publisher_info a")
        if not name_tag:
            continue
        raw_title = name_tag.get_text(strip=True)
        title = clean_title(raw_title)
        author = author_tag.get_text(strip=True) if author_tag else ""
        if title and is_chinese_title(title):
            items.append({"title": title, "author": author, "source": "当当·近7日畅销",
                          "category": infer_category(title)})
        if len(items) >= MAX_BOOKS:
            break

    print(f"  ✅ 抓到 {len(items)} 本")
    return items


# ──────────────────────────────────────────────
# 数据源 2：豆瓣图书热门
# ──────────────────────────────────────────────
def fetch_douban() -> list[dict]:
    # 豆瓣图书 chart 页面
    url = "https://book.douban.com/chart"
    print("📚 [2/4] 豆瓣热门图书...")
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    items = []
    for div in soup.select(".subject-item, .article"):
        title_tag = div.select_one("h2 a, .title a")
        pub_tag = div.select_one(".pub")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        pub_info = pub_tag.get_text(strip=True) if pub_tag else ""
        author = pub_info.split("/")[0].strip() if pub_info else ""
        if title and is_chinese_title(title):
            items.append({"title": title, "author": author, "source": "豆瓣·热门",
                          "category": infer_category(title)})
        if len(items) >= MAX_BOOKS:
            break

    print(f"  ✅ 抓到 {len(items)} 本")
    return items


# ──────────────────────────────────────────────
# 数据源 3：豆瓣新书速递
# ──────────────────────────────────────────────
def fetch_douban_new() -> list[dict]:
    url = "https://book.douban.com/latest"
    print("📚 [3/4] 豆瓣新书速递...")
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    items = []
    for li in soup.select("li.subject-item"):
        title_tag = li.select_one("h2 a")
        pub_tag = li.select_one(".pub")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        pub_info = pub_tag.get_text(strip=True) if pub_tag else ""
        author = pub_info.split("/")[0].strip() if pub_info else ""
        if title and is_chinese_title(title):
            items.append({"title": title, "author": author, "source": "豆瓣·新书速递",
                          "category": infer_category(title)})
        if len(items) >= MAX_BOOKS:
            break

    print(f"  ✅ 抓到 {len(items)} 本")
    return items


# ──────────────────────────────────────────────
# 数据源 4：微信读书热搜
# ──────────────────────────────────────────────
def fetch_weread() -> list[dict]:
    # 微信读书榜单 API（免登录可访问）
    url = "https://weread.qq.com/web/booklistdetail?booklistId=7289&maxIdx=0&count=30"
    print("📚 [4/4] 微信读书榜单...")
    try:
        resp = requests.get(url, headers={
            **HEADERS,
            "Referer": "https://weread.qq.com/"
        }, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = []
            for item in (data.get("books") or data.get("items") or []):
                book = item.get("bookInfo") or item
                title = book.get("title", "")
                author = book.get("author", "")
                if title and is_chinese_title(title):
                    items.append({"title": title, "author": author, "source": "微信读书·榜单",
                                  "category": infer_category(title)})
                if len(items) >= MAX_BOOKS:
                    break
            print(f"  ✅ 抓到 {len(items)} 本")
            return items
    except Exception as e:
        print(f"  ⚠ 微信读书失败: {e}")
    return []


# ──────────────────────────────────────────────
# 去重合并，最多取 MAX_BOOKS 本
# ──────────────────────────────────────────────
def merge_and_dedupe(*lists) -> list[dict]:
    seen = set()
    result = []
    for lst in lists:
        for book in lst:
            key = re.sub(r'\s+', '', book["title"])
            if key and key not in seen:
                seen.add(key)
                result.append(book)
            if len(result) >= MAX_BOOKS:
                return result
    return result


# ──────────────────────────────────────────────
# 生成 HTML
# ──────────────────────────────────────────────
def generate_html(books: list[dict], generated_at: str) -> str:
    source_colors = {
        "当当·近7日畅销": "#fef3c7;color:#d97706",
        "豆瓣·热门":      "#dbeafe;color:#2563eb",
        "豆瓣·新书速递":  "#d1fae5;color:#059669",
        "微信读书·榜单":  "#ede9fe;color:#7c3aed",
    }

    rows = ""
    for i, book in enumerate(books, 1):
        link = zlib_link(book["title"])
        author_cell = book.get("author") or "—"
        src = book.get("source", "")
        sc = source_colors.get(src, "#f3f4f6;color:#374151")
        bg, fg = sc.split(";color:")
        source_badge = f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:4px;font-size:.75rem">{src}</span>'
        rows += f"""
        <tr>
          <td class="num">{i}</td>
          <td class="title">{book['title']}</td>
          <td class="author">{author_cell}</td>
          <td>{source_badge}</td>
          <td class="zlib"><a href="{link}" target="_blank">搜索 📖</a></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>国内热门书单 · {generated_at}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: "PingFang SC","Microsoft YaHei",sans-serif; background: #f0f2f5; color: #333; }}
  .header {{ background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color: #fff; padding: 28px 40px; }}
  .header h1 {{ font-size: 1.7rem; font-weight: 800; letter-spacing:.02em }}
  .header p {{ margin-top: 8px; font-size: .88rem; opacity: .85; }}
  .container {{ max-width: 1000px; margin: 28px auto; padding: 0 16px; }}
  .tip {{ background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;
          padding: 12px 18px; margin-bottom: 20px; font-size: .85rem; color: #92400e; line-height:1.6 }}
  .card {{ background: #fff; border-radius: 14px; box-shadow: 0 2px 16px rgba(0,0,0,.08); overflow: hidden; }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead {{ background: #f8f8fa; }}
  th {{ padding: 13px 14px; font-size: .78rem; color: #888; text-align: left;
        text-transform: uppercase; letter-spacing: .05em; border-bottom: 2px solid #f0f0f0; }}
  td {{ padding: 12px 14px; font-size: .9rem; border-top: 1px solid #f5f5f5; vertical-align: middle; }}
  tr:hover td {{ background: #fafbff; }}
  .num {{ width: 40px; color: #bbb; text-align: center; font-weight: 700; font-size:.95rem }}
  tr:nth-child(-n+3) .num {{ color:#f59e0b; font-size:1.05rem }}
  .title {{ font-weight: 600; color: #1a1a2e; max-width: 280px; }}
  .author {{ color: #666; font-size: .84rem; }}
  .zlib a {{ color: #6366f1; text-decoration: none; font-weight: 600; }}
  .zlib a:hover {{ text-decoration: underline; }}
  .footer {{ text-align: center; padding: 22px; color: #bbb; font-size: .8rem; }}
  .stat-bar {{ display:flex; gap:14px; margin-bottom:20px; flex-wrap:wrap; }}
  .stat {{ background:#fff; border-radius:10px; padding:12px 20px; flex:1; min-width:140px;
           box-shadow:0 1px 6px rgba(0,0,0,.06); text-align:center; }}
  .stat .n {{ font-size:1.6rem; font-weight:800; color:#6366f1; }}
  .stat .l {{ font-size:.78rem; color:#888; margin-top:2px; }}
</style>
</head>
<body>
<div class="header">
  <h1>📚 国内热门书单</h1>
  <p>数据来源：当当网 · 豆瓣图书 · 微信读书 &nbsp;|&nbsp; 生成时间：{generated_at}</p>
</div>
<div class="container">
  <div class="stat-bar">
    <div class="stat"><div class="n">{len(books)}</div><div class="l">本书入榜</div></div>
    <div class="stat"><div class="n">{len(set(b['source'] for b in books))}</div><div class="l">个数据来源</div></div>
    <div class="stat"><div class="n">{len([b for b in books if b.get('author')])}</div><div class="l">本有作者信息</div></div>
  </div>
  <div class="tip">
    💡 点击「搜索 📖」跳转 Z-Library 中文搜索（书名精准匹配，优先中文版）。
    若搜索无结果，可去掉副标题后重试。域名失效时可换 <code>zlibrary.to</code> 或 <code>z-lib.fm</code>。
  </div>
  <div class="card">
    <table>
      <thead>
        <tr>
          <th>#</th><th>书名</th><th>作者</th><th>来源榜单</th><th>Z-Library</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>
  </div>
  <div class="footer">共 {len(books)} 本 · 每次运行自动更新 · 链接仅作搜索用途</div>
</div>
</body>
</html>"""


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────
def main():
    print("=" * 52)
    print(f"🚀 国内热门书单追踪器 v2  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 52)

    dd   = fetch_dangdang()
    db   = fetch_douban()
    dbnew = fetch_douban_new()
    wr   = fetch_weread()

    books = merge_and_dedupe(dd, db, dbnew, wr)

    if not books:
        print("\n❌ 所有数据源均未返回数据，请检查网络后重试。")
        sys.exit(1)

    print(f"\n📊 最终书单：{len(books)} 本（已去重）")

    generated_at = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    html = generate_html(books, generated_at)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ HTML 报告已保存：{OUTPUT_HTML}")
    print("\n📋 前10本预览：")
    for i, b in enumerate(books[:10], 1):
        print(f"  {i:2d}. {b['title']:<28}  {b.get('author','')}")

    # 输出 JSON（供 inject_books.py 使用）
    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON 书单已保存：books.json")

    return OUTPUT_HTML


if __name__ == "__main__":
    main()
