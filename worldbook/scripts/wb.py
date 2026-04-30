#!/usr/bin/env python3
"""Worldbook CLI - 角色扮演游戏世界观设定管理。

用法: python scripts/wb.py <命令> [参数]

命令:
  init              创建新世界书
  list-wbs          列出所有世界书
  create-entry      创建新条目
  get-entry         查看条目详情
  update-entry      更新条目
  delete-entry      删除条目
  list-entries      列出条目
  search            搜索条目
  toggle-entry      启用/禁用一个条目
  export            导出世界书
  import            导入世界书
  summary           世界书概览
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ─── 路径工具 ───────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"


def get_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def get_wb_path(name: str) -> Path:
    return get_data_dir() / f"{name}.json"


# ─── 世界书 I/O ─────────────────────────────────────────────

CATEGORIES = ["地点", "人物", "组织", "历史", "魔法", "种族", "物品", "其他"]


def load_wb(name: str) -> dict:
    path = get_wb_path(name)
    if not path.exists():
        sys.exit(f'错误: 世界书 "{name}" 不存在。使用 "list-wbs" 查看可用世界书。')
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_wb(name: str, data: dict):
    path = get_wb_path(name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_entry(wb: dict, key: str) -> dict:
    entries = wb.get("entries", {})
    if key not in entries:
        wb_name = wb["meta"]["name"]
        available = ", ".join(sorted(entries.keys())) or "(无)"
        sys.exit(f'错误: 条目 "{key}" 在世界书 "{wb_name}" 中不存在。可用条目: {available}')
    return entries[key]


# ─── 搜索逻辑 ───────────────────────────────────────────────

def match_score(query: str, keyword: str) -> int:
    """计算匹配分数：精确匹配 > 前缀匹配 > 子串匹配。"""
    q = query.lower()
    kw = keyword.lower()
    if q == kw:
        return 3
    if kw.startswith(q):
        return 2
    if q in kw:
        return 1
    return 0


def search_entries(wb: dict, query: str) -> list:
    """搜索世界书，返回匹配条目列表（按 score+order 排序）。"""
    results = []
    for key, entry in wb.get("entries", {}).items():
        if not entry.get("enabled", True):
            continue
        # 在 title 和 keywords 中搜索
        best = max(
            match_score(query, entry.get("title", "")),
            *(match_score(query, kw.strip()) for kw in entry.get("keywords", "").split(",")),
        )
        if best > 0:
            results.append((best, entry.get("order", 10), key, entry))
    # 按分数降序、order 降序、key 升序
    results.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return [r[3] for r in results]


# ─── 格式化输出 ─────────────────────────────────────────────

def format_entry(key: str, entry: dict) -> str:
    lines = [
        f"[{key}] {entry['title']}",
        f"  分类: {entry.get('category', '未分类')}  |  优先级: {entry.get('order', 10)}  |  状态: {'启用' if entry.get('enabled', True) else '禁用'}",
        f"  关键词: {entry.get('keywords', '')}",
        f"  内容: {entry.get('content', '')}",
    ]
    return "\n".join(lines)


# ─── 命令处理函数 ──────────────────────────────────────────

def cmd_init(args):
    path = get_wb_path(args.name)
    if path.exists() and not args.force:
        sys.exit(f'错误: 世界书 "{args.name}" 已存在。使用 --force 覆盖。')
    wb = {
        "meta": {
            "name": args.name,
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "version": 1,
        },
        "entries": {},
    }
    save_wb(args.name, wb)
    print(f'世界书 "{args.name}" 已创建。')


def cmd_list_wbs(args):
    data_dir = get_data_dir()
    files = sorted(data_dir.glob("*.json"))
    if not files:
        print("(没有世界书)")
        return
    for f in files:
        try:
            wb = json.loads(f.read_text(encoding="utf-8"))
            name = wb["meta"]["name"]
            count = len(wb.get("entries", {}))
            print(f"  {name}  ({count} 个条目)")
        except Exception:
            print(f"  {f.stem}  (数据已损坏)")


def cmd_create_entry(args):
    wb = load_wb(args.wb)
    entries = wb.setdefault("entries", {})

    if args.key in entries:
        sys.exit(f'错误: 条目 "{args.key}" 已存在。')

    if args.category and args.category not in CATEGORIES:
        print(f'警告: 分类 "{args.category}" 不在预设列表中 ({", ".join(CATEGORIES)})，将作为自定义分类。')

    entries[args.key] = {
        "title": args.title or args.key,
        "keywords": args.keywords or args.key,
        "category": args.category or "其他",
        "content": args.content or "",
        "order": args.order or 10,
        "enabled": True,
    }
    save_wb(args.wb, wb)
    print(f'条目 "{args.key}" ({entries[args.key]["title"]}) 已创建。')


def cmd_get_entry(args):
    wb = load_wb(args.wb)
    entry = get_entry(wb, args.key)

    if args.json:
        print(json.dumps({args.key: entry}, ensure_ascii=False, indent=2))
    else:
        print(format_entry(args.key, entry))


def cmd_update_entry(args):
    wb = load_wb(args.wb)
    entry = get_entry(wb, args.key)

    if args.title is not None:
        entry["title"] = args.title
    if args.keywords is not None:
        entry["keywords"] = args.keywords
    if args.category is not None:
        if args.category not in CATEGORIES:
            print(f'警告: 分类 "{args.category}" 不在预设列表中 ({", ".join(CATEGORIES)})。')
        entry["category"] = args.category
    if args.content is not None:
        entry["content"] = args.content
    if args.order is not None:
        entry["order"] = args.order

    save_wb(args.wb, wb)
    print(f'条目 "{args.key}" ({entry["title"]}) 已更新。')


def cmd_delete_entry(args):
    wb = load_wb(args.wb)
    entry = get_entry(wb, args.key)
    title = entry["title"]
    del wb["entries"][args.key]
    save_wb(args.wb, wb)
    print(f'条目 "{args.key}" ({title}) 已删除。')


def cmd_list_entries(args):
    wb = load_wb(args.wb)
    entries = wb.get("entries", {})
    if not entries:
        print("(无条目)")
        return

    filtered = entries
    if args.category:
        filtered = {k: v for k, v in entries.items() if v.get("category") == args.category}

    if not filtered:
        print(f'(分类 "{args.category}" 下无条目)')
        return

    # 按 order 降序排列
    sorted_entries = sorted(filtered.items(), key=lambda x: -x[1].get("order", 10))
    for key, entry in sorted_entries:
        status = "[+]" if entry.get("enabled", True) else "[-]"
        print(f"  {status} [{key}] {entry['title']}  —  {entry.get('category', '未分类')}  (优先级 {entry.get('order', 10)})")


def cmd_search(args):
    wb = load_wb(args.wb)
    results = search_entries(wb, args.query)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        print(f'未找到与 "{args.query}" 匹配的条目。')
        return

    print(f'搜索 "{args.query}" 找到 {len(results)} 个结果:')
    print()
    for entry in results:
        # 找到 entry 的 key
        for k, v in wb["entries"].items():
            if v is entry:
                print(format_entry(k, entry))
                print()
                break


def cmd_toggle_entry(args):
    wb = load_wb(args.wb)
    entry = get_entry(wb, args.key)
    new_state = not entry.get("enabled", True)
    entry["enabled"] = new_state
    save_wb(args.wb, wb)
    state_str = "启用" if new_state else "禁用"
    print(f'条目 "{args.key}" ({entry["title"]}) 已{state_str}。')


def cmd_export(args):
    wb = load_wb(args.wb)
    out_path = args.file or str(get_data_dir() / f"{args.wb}_export.json")

    if Path(out_path).exists() and not args.force:
        sys.exit(f'错误: 文件 "{out_path}" 已存在。使用 --force 覆盖。')

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(wb, f, ensure_ascii=False, indent=2)
    print(f'世界书 "{args.wb}" 已导出到: {out_path}')


def cmd_import(args):
    import_path = Path(args.file)
    if not import_path.exists():
        sys.exit(f'错误: 文件 "{args.file}" 不存在。')

    try:
        data = json.loads(import_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"错误: 文件不是有效的 JSON: {e}")

    if "meta" not in data or "entries" not in data:
        sys.exit('错误: 文件不是有效的世界书（缺少 "meta" 或 "entries" 键）。')

    target_name = args.wb or data["meta"]["name"]
    target_path = get_wb_path(target_name)

    if target_path.exists() and not args.force:
        sys.exit(f'错误: 世界书 "{target_name}" 已存在。使用 --force 覆盖。')

    data["meta"]["name"] = target_name
    save_wb(target_name, data)
    print(f'世界书 "{target_name}" 已导入 ({len(data.get("entries", {}))} 个条目)。')


def cmd_summary(args):
    wb = load_wb(args.wb)
    meta = wb["meta"]
    entries = wb.get("entries", {})

    lines = [
        f"世界书: {meta['name']}",
        f"创建时间: {meta['created']}",
        f"条目数: {len(entries)}",
        "",
    ]

    if not entries:
        lines.append("  (无条目)")
    else:
        # 按分类统计
        cat_count = {}
        enabled_count = 0
        for entry in entries.values():
            cat = entry.get("category", "未分类")
            cat_count[cat] = cat_count.get(cat, 0) + 1
            if entry.get("enabled", True):
                enabled_count += 1

        lines.append(f"  已启用: {enabled_count} / {len(entries)}")
        lines.append("  分类统计:")
        for cat in CATEGORIES:
            if cat in cat_count:
                lines.append(f"    {cat}: {cat_count[cat]} 条")
        for cat, count in sorted(cat_count.items()):
            if cat not in CATEGORIES:
                lines.append(f"    {cat}(自定义): {count} 条")

    print("\n".join(lines))


# ─── 主入口 ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Worldbook CLI - 世界观设定管理")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    # init
    p = sub.add_parser("init", help="创建新世界书")
    p.add_argument("name", help="世界书名称")
    p.add_argument("--force", action="store_true", help="覆盖已存在的世界书")
    p.set_defaults(func=cmd_init)

    # list-wbs
    p = sub.add_parser("list-wbs", help="列出所有世界书")
    p.set_defaults(func=cmd_list_wbs)

    # create-entry
    p = sub.add_parser("create-entry", help="创建新条目")
    p.add_argument("key", help="条目键名（英文，唯一标识）")
    p.add_argument("--title", help="显示标题")
    p.add_argument("--keywords", help="触发关键词，逗号分隔")
    p.add_argument("--category", help=f'分类标签: {", ".join(CATEGORIES)}')
    p.add_argument("--content", help="条目正文（世界观描述）")
    p.add_argument("--order", type=int, default=10, help="排序优先级 (默认: 10)")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.set_defaults(func=cmd_create_entry)

    # get-entry
    p = sub.add_parser("get-entry", help="查看条目详情")
    p.add_argument("key", help="条目键名")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    p.set_defaults(func=cmd_get_entry)

    # update-entry
    p = sub.add_parser("update-entry", help="更新条目")
    p.add_argument("key", help="条目键名")
    p.add_argument("--title", help="新标题")
    p.add_argument("--keywords", help="新关键词")
    p.add_argument("--category", help="新分类")
    p.add_argument("--content", help="新正文内容")
    p.add_argument("--order", type=int, help="新优先级")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.set_defaults(func=cmd_update_entry)

    # delete-entry
    p = sub.add_parser("delete-entry", help="删除条目")
    p.add_argument("key", help="条目键名")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.set_defaults(func=cmd_delete_entry)

    # list-entries
    p = sub.add_parser("list-entries", help="列出条目")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.add_argument("--category", help="按分类过滤")
    p.set_defaults(func=cmd_list_entries)

    # search
    p = sub.add_parser("search", help="搜索条目")
    p.add_argument("query", help="搜索词（在标题和关键词中匹配）")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    p.set_defaults(func=cmd_search)

    # toggle-entry
    p = sub.add_parser("toggle-entry", help="启用/禁用一个条目")
    p.add_argument("key", help="条目键名")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.set_defaults(func=cmd_toggle_entry)

    # export
    p = sub.add_parser("export", help="导出世界书为 JSON 文件")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.add_argument("--file", help="输出文件路径")
    p.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    p.set_defaults(func=cmd_export)

    # import
    p = sub.add_parser("import", help="从 JSON 文件导入世界书")
    p.add_argument("--file", required=True, help="要导入的 JSON 文件路径")
    p.add_argument("--wb", default=None, help="目标世界书名称 (默认: 使用 JSON 中的名称)")
    p.add_argument("--force", action="store_true", help="覆盖已存在的世界书")
    p.set_defaults(func=cmd_import)

    # summary
    p = sub.add_parser("summary", help="世界书概览")
    p.add_argument("--wb", default="default", help="世界书名称 (默认: default)")
    p.set_defaults(func=cmd_summary)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
