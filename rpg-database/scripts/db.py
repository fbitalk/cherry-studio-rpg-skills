#!/usr/bin/env python3
"""RPG Database CLI - 角色扮演游戏结构化表格数据库。

用法: python scripts/db.py <命令> [参数]

命令:
  init              创建新数据库
  list-dbs          列出所有数据库
  list-tables       列出数据库中的表
  create-table      创建新表格
  get-table         查看表格数据
  update-cell       更新单个单元格
  update-row        更新整行数据
  insert-row        插入新行
  delete-row        删除行
  delete-table      删除表格
  export            导出数据库
  import            导入数据库
  summary           数据库概览
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# ─── 路径工具 ───────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"


def get_data_dir():
    """获取 data 目录，不存在则创建。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def get_db_path(name: str) -> Path:
    return get_data_dir() / f"{name}.json"


# ─── 数据库 I/O ──────────────────────────────────────────────

def load_db(name: str) -> dict:
    """加载数据库，文件不存在时退出。"""
    path = get_db_path(name)
    if not path.exists():
        sys.exit(f'错误: 数据库 "{name}" 不存在。使用 "list-dbs" 查看可用数据库。')
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(name: str, data: dict):
    """保存数据库到 JSON 文件。"""
    path = get_db_path(name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_table(db: dict, table_name: str) -> dict:
    """获取表格，不存在时退出。"""
    tables = db.get("tables", {})
    if table_name not in tables:
        db_name = db["meta"]["name"]
        available = ", ".join(tables.keys()) or "(无)"
        sys.exit(f'错误: 表 "{table_name}" 在数据库 "{db_name}" 中不存在。可用表: {available}')
    return tables[table_name]


def resolve_row_index(table: dict, row_spec: str) -> int:
    """解析行索引（支持数字和 last 关键字）。"""
    rows = table["rows"]
    if row_spec == "last":
        if not rows:
            sys.exit(f'错误: 表 "{table["name"]}" 为空，没有可操作的行。')
        return len(rows) - 1
    try:
        idx = int(row_spec)
    except ValueError:
        sys.exit(f'错误: 行索引必须是整数或 "last"，收到: {row_spec}')
    if idx < 0 or idx >= len(rows):
        sys.exit(f'错误: 行索引 {idx} 超出范围。表 "{table["name"]}" 有 {len(rows)} 行 (0-{len(rows)-1})。')
    return idx


def resolve_col_index(table: dict, col_spec: str) -> int:
    """解析列索引（支持数字和列名）。"""
    headers = table["headers"]
    try:
        idx = int(col_spec)
        if 0 <= idx < len(headers):
            return idx
    except ValueError:
        for i, h in enumerate(headers):
            if h == col_spec:
                return i
        sys.exit(f'错误: 列 "{col_spec}" 不存在。可用列: {", ".join(headers)}')
    sys.exit(f'错误: 列索引 {col_spec} 超出范围。可用: 0-{len(headers)-1}')


# ─── 格式化输出 ─────────────────────────────────────────────

def format_table(table: dict) -> str:
    """将表格格式化为人类可读的文本。"""
    headers = table["headers"]
    rows = table["rows"]
    if not headers:
        return "(空表，无列头)"

    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    lines = []
    # 表头
    header_line = "  " + "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    # 分隔线
    sep_line = "  " + "  ".join("-" * col_widths[i] for i in range(len(headers)))
    lines.append(sep_line)
    # 数据行
    for ri, row in enumerate(rows):
        padded = []
        for i in range(len(headers)):
            val = str(row[i]) if i < len(row) else ""
            padded.append(val.ljust(col_widths[i]))
        lines.append(f"  {ri}: {'  '.join(padded)}")

    return "\n".join(lines)


def format_summary(db: dict) -> str:
    """格式化数据库概览。"""
    meta = db["meta"]
    tables = db.get("tables", {})
    lines = [
        f"数据库: {meta['name']}",
        f"创建时间: {meta['created']}",
        f"表格数: {len(tables)}",
        "",
    ]
    if not tables:
        lines.append("  (无表格)")
    else:
        for key, t in tables.items():
            lines.append(f"  [{key}] {t['name']}  —  {len(t['rows'])} 行, {len(t['headers'])} 列")
            if t.get("notes"):
                lines.append(f"    备注: {t['notes']}")
    return "\n".join(lines)


# ─── 命令处理函数 ──────────────────────────────────────────

def cmd_init(args):
    """创建新数据库。"""
    path = get_db_path(args.name)
    if path.exists() and not args.force:
        sys.exit(f'错误: 数据库 "{args.name}" 已存在。使用 --force 覆盖。')

    db = {
        "meta": {
            "name": args.name,
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "version": 1,
        },
        "tables": {},
    }
    save_db(args.name, db)
    print(f'数据库 "{args.name}" 已创建。')


def cmd_list_dbs(args):
    """列出所有数据库。"""
    data_dir = get_data_dir()
    files = sorted(data_dir.glob("*.json"))
    if not files:
        print("(没有数据库)")
        return
    for f in files:
        try:
            db = json.loads(f.read_text(encoding="utf-8"))
            name = db["meta"]["name"]
            tables = len(db.get("tables", {}))
            print(f"  {name}  ({tables} 个表)")
        except Exception:
            print(f"  {f.stem}  (数据已损坏)")


def cmd_list_tables(args):
    """列出数据库中的所有表。"""
    db = load_db(args.db)
    tables = db.get("tables", {})
    if not tables:
        print("(无表格)")
        return
    for key, t in tables.items():
        print(f"  [{key}] {t['name']}  —  {len(t['rows'])} 行 x {len(t['headers'])} 列")


def cmd_create_table(args):
    """创建新表格。"""
    db = load_db(args.db)
    tables = db.setdefault("tables", {})

    if args.name in tables:
        sys.exit(f'错误: 表 "{args.name}" 已存在。')

    headers = [h.strip() for h in args.headers.split(",")]
    tables[args.name] = {
        "name": args.name,
        "headers": headers,
        "rows": [],
        "notes": args.notes or "",
    }
    save_db(args.db, db)
    print(f'表 "{args.name}" 已创建 ({len(headers)} 列: {", ".join(headers)})。')


def cmd_get_table(args):
    """查看表格数据。"""
    db = load_db(args.db)
    table = get_table(db, args.name)

    if args.json:
        print(json.dumps(table, ensure_ascii=False, indent=2))
    else:
        print(f'[{args.name}] {table["name"]}  ({len(table["rows"])} 行 x {len(table["headers"])} 列)')
        if table.get("notes"):
            print(f'备注: {table["notes"]}')
        print()
        print(format_table(table))


def cmd_update_cell(args):
    """更新单个单元格。"""
    db = load_db(args.db)
    table = get_table(db, args.name)
    row_idx = resolve_row_index(table, args.row)
    col_idx = resolve_col_index(table, args.col)

    old_val = table["rows"][row_idx][col_idx] if col_idx < len(table["rows"][row_idx]) else ""
    table["rows"][row_idx][col_idx] = args.value
    save_db(args.db, db)
    print(f'表 "{args.name}" 行 {row_idx} 列 "{table["headers"][col_idx]}" 已更新: {old_val} → {args.value}')


def cmd_update_row(args):
    """更新整行数据。"""
    db = load_db(args.db)
    table = get_table(db, args.name)
    row_idx = resolve_row_index(table, args.row)

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        sys.exit(f"错误: --data 不是有效的 JSON: {e}")

    headers = table["headers"]
    # 校验列名
    for key in data:
        if key not in headers:
            sys.exit(f'错误: 列 "{key}" 不存在。可用列: {", ".join(headers)}')

    row = table["rows"][row_idx]
    for key, val in data.items():
        col_idx = headers.index(key)
        row[col_idx] = str(val)

    save_db(args.db, db)
    print(f'表 "{args.name}" 行 {row_idx} 已更新 ({len(data)} 个字段)。')


def cmd_insert_row(args):
    """插入新行（表尾追加）。"""
    db = load_db(args.db)
    table = get_table(db, args.name)

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        sys.exit(f"错误: --data 不是有效的 JSON: {e}")

    headers = table["headers"]
    # 校验列名
    for key in data:
        if key not in headers:
            sys.exit(f'错误: 列 "{key}" 不存在。可用列: {", ".join(headers)}')

    new_row = [""] * len(headers)
    for key, val in data.items():
        col_idx = headers.index(key)
        new_row[col_idx] = str(val)

    table["rows"].append(new_row)
    new_idx = len(table["rows"]) - 1
    save_db(args.db, db)
    print(f'表 "{args.name}" 已插入新行 (索引 {new_idx})。')


def cmd_delete_row(args):
    """删除行。"""
    db = load_db(args.db)
    table = get_table(db, args.name)
    row_idx = resolve_row_index(table, args.row)

    removed = table["rows"].pop(row_idx)
    save_db(args.db, db)
    print(f'表 "{args.name}" 行 {row_idx} 已删除。内容: {removed}')


def cmd_delete_table(args):
    """删除表格。"""
    db = load_db(args.db)
    table = get_table(db, args.name)  # 验证存在

    del db["tables"][args.name]
    save_db(args.db, db)
    print(f'表 "{args.name}" ({table["name"]}) 已从数据库 "{db["meta"]["name"]}" 中删除。')


def cmd_export(args):
    """导出数据库为 JSON 文件。"""
    db = load_db(args.db)
    out_path = args.file or str(get_data_dir() / f"{args.db}_export.json")

    if Path(out_path).exists() and not args.force:
        sys.exit(f'错误: 文件 "{out_path}" 已存在。使用 --force 覆盖。')

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f'数据库 "{args.db}" 已导出到: {out_path}')


def cmd_import(args):
    """从 JSON 文件导入数据库。"""
    import_path = Path(args.file)
    if not import_path.exists():
        sys.exit(f'错误: 文件 "{args.file}" 不存在。')

    try:
        data = json.loads(import_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"错误: 文件不是有效的 JSON: {e}")

    # 验证结构
    if "meta" not in data or "tables" not in data:
        sys.exit('错误: 文件不是有效的 RPG 数据库（缺少 "meta" 或 "tables" 键）。')

    target_name = args.db or data["meta"]["name"]
    target_path = get_db_path(target_name)

    if target_path.exists() and not args.force:
        sys.exit(f'错误: 数据库 "{target_name}" 已存在。使用 --force 覆盖。')

    data["meta"]["name"] = target_name
    save_db(target_name, data)
    print(f'数据库 "{target_name}" 已导入 ({len(data.get("tables", {}))} 个表)。')


def cmd_summary(args):
    """打印数据库概览。"""
    db = load_db(args.db)
    print(format_summary(db))


# ─── 主入口 ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RPG Database CLI - 角色扮演游戏结构化表格数据库",
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    # init
    p = sub.add_parser("init", help="创建新数据库")
    p.add_argument("name", help="数据库名称")
    p.add_argument("--force", action="store_true", help="覆盖已存在的数据库")
    p.set_defaults(func=cmd_init)

    # list-dbs
    p = sub.add_parser("list-dbs", help="列出所有数据库")
    p.set_defaults(func=cmd_list_dbs)

    # list-tables
    p = sub.add_parser("list-tables", help="列出数据库中的表")
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.set_defaults(func=cmd_list_tables)

    # create-table
    p = sub.add_parser("create-table", help="创建新表格")
    p.add_argument("name", help="表格键名（英文）")
    p.add_argument("--headers", required=True, help='列头，逗号分隔，如 "属性名,当前值,最大值"')
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.add_argument("--notes", default="", help="表格备注")
    p.set_defaults(func=cmd_create_table)

    # get-table
    p = sub.add_parser("get-table", help="查看表格数据")
    p.add_argument("name", help="表格键名")
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    p.set_defaults(func=cmd_get_table)

    # update-cell
    p = sub.add_parser("update-cell", help="更新单个单元格")
    p.add_argument("name", help="表格键名")
    p.add_argument("row", help='行索引 (0-based) 或 "last"')
    p.add_argument("col", help="列索引或列名")
    p.add_argument("value", help="新值")
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.set_defaults(func=cmd_update_cell)

    # update-row
    p = sub.add_parser("update-row", help="更新整行数据")
    p.add_argument("name", help="表格键名")
    p.add_argument("row", help='行索引 (0-based) 或 "last"')
    p.add_argument("--data", required=True, help='JSON 对象，如 \'{"属性名":"生命值","当前值":"80"}\'')
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.set_defaults(func=cmd_update_row)

    # insert-row
    p = sub.add_parser("insert-row", help="插入新行")
    p.add_argument("name", help="表格键名")
    p.add_argument("--data", required=True, help='JSON 对象，如 \'{"物品名称":"治疗药水","数量":"3"}\'')
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.set_defaults(func=cmd_insert_row)

    # delete-row
    p = sub.add_parser("delete-row", help="删除行")
    p.add_argument("name", help="表格键名")
    p.add_argument("row", help='行索引 (0-based) 或 "last"')
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.set_defaults(func=cmd_delete_row)

    # delete-table
    p = sub.add_parser("delete-table", help="删除表格")
    p.add_argument("name", help="表格键名")
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.set_defaults(func=cmd_delete_table)

    # export
    p = sub.add_parser("export", help="导出数据库为 JSON 文件")
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.add_argument("--file", help="输出文件路径")
    p.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    p.set_defaults(func=cmd_export)

    # import
    p = sub.add_parser("import", help="从 JSON 文件导入数据库")
    p.add_argument("--file", required=True, help="要导入的 JSON 文件路径")
    p.add_argument("--db", default=None, help="目标数据库名称 (默认: 使用 JSON 中的名称)")
    p.add_argument("--force", action="store_true", help="覆盖已存在的数据库")
    p.set_defaults(func=cmd_import)

    # summary
    p = sub.add_parser("summary", help="数据库概览")
    p.add_argument("--db", default="default", help="数据库名称 (默认: default)")
    p.set_defaults(func=cmd_summary)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
