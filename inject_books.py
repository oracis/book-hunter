#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_books.py
读取 books.json，自动注入到 src/index.js 和 public/index.html
用法: python inject_books.py
"""

import json
import re
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_JSON = os.path.join(BASE_DIR, "books.json")
SRC_JS = os.path.join(BASE_DIR, "src", "index.js")
PUBLIC_HTML = os.path.join(BASE_DIR, "public", "index.html")


def format_js_array(books):
    """把 books 列表格式化为 JS 数组字符串（4 空格缩进，与 public/index.html 格式一致）"""
    lines = ["const BOOKS = ["]
    for i, b in enumerate(books):
        title = b["title"].replace("'", "\\'")
        author = (b.get("author") or "").replace("'", "\\'")
        source = (b.get("source") or "").replace("'", "\\'")
        rating = b.get("rating", "")
        year = b.get("year", "")
        category = b.get("category") or ""
        # 如果没有 category，打个警告
        if not category:
            print(f"  ⚠ 缺 category: {title}")
        entry = (
            "    {{ title: '{}', author: '{}', "
            "source: '{}', rating: '{}', year: '{}', category: '{}' }}"
        ).format(title, author, source, rating, year, category)
        if i < len(books) - 1:
            entry += ","
        lines.append(entry)
    lines.append("    ];")
    return "\n".join(lines)


def update_src_js(books_js_str):
    with open(SRC_JS, "r", encoding="utf-8") as f:
        content = f.read()
    # 支持 ]; 前面有缩进的情况
    pattern = r"const BOOKS = \[[\s\S]*?\n\s*\];"
    new_content = re.sub(pattern, books_js_str, content, count=1)
    if new_content == content:
        print("  ❌ src/index.js: 未找到 BOOKS 数组，请检查格式")
        return False
    with open(SRC_JS, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  ✅ 已更新 src/index.js（{len(books_js_str.splitlines())} 行）")
    return True


def update_public_html(books_js_str):
    with open(PUBLIC_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    # 支持 ]; 前面有缩进的情况
    pattern = r"const BOOKS = \[[\s\S]*?\n\s*\];"
    new_content = re.sub(pattern, books_js_str, content, count=1)
    if new_content == content:
        print("  ❌ public/index.html: 未找到 BOOKS 数组，请检查格式")
        return False
    with open(PUBLIC_HTML, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  ✅ 已更新 public/index.html（{len(books_js_str.splitlines())} 行）")
    return True


def main():
    print("=" * 50)
    print("📚 inject_books.py - 注入书单到前端")
    print("=" * 50)

    # 1. 读取 books.json
    if not os.path.exists(BOOKS_JSON):
        print(f"❌ 找不到 {BOOKS_JSON}")
        print("   请先运行: python booklist_tracker.py")
        sys.exit(1)

    with open(BOOKS_JSON, "r", encoding="utf-8") as f:
        books = json.load(f)
    print(f"📖 读取到 {len(books)} 本书")

    # 2. 格式化为 JS
    books_js_str = format_js_array(books)
    print(f"📝 格式化为 JS 数组（{len(books_js_str.splitlines())} 行）")

    # 3. 更新 src/index.js
    print("\n[1/2] 更新 src/index.js ...")
    ok1 = update_src_js(books_js_str)

    # 4. 更新 public/index.html
    print("\n[2/2] 更新 public/index.html ...")
    ok2 = update_public_html(books_js_str)

    print()
    if ok1 and ok2:
        print(f"🎉 全部完成！{len(books)} 本书已注入到两个文件。")
        print("   记得 git commit + git push 触发部署！")
    else:
        print("⚠ 部分文件更新失败，请检查上面的错误信息。")
        sys.exit(1)


if __name__ == "__main__":
    main()
