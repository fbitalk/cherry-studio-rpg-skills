#!/usr/bin/env python3
"""
游戏数据库可视化前端 — 生成自包含 HTML 卡片

用法:
    python scripts/viz.py [--db <数据库名>]

输出写入 stdout，Cherry Studio 的 HtmlArtifactsCard 自动渲染。
"""

import argparse
import json
import os
import sys
import html as html_mod

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

TABLE_DISPLAY_NAMES = {
    'global-state': '🌍 全局状态',
    'protagonist-info': '👤 主角信息',
    'character-stats': '📊 角色属性',
    'inventory': '🎒 背包物品',
    'quests': '📋 任务日志',
    'npc-relations': '🤝 角色关系',
    'protagonist-skills': '⚡ 主角技能',
    'skills': '⚡ 技能列表',
    'equipment': '🛡️ 装备栏',
    'memo': '📝 备忘录',
    'factions': '🏰 势力表',
    'locations': '📍 地点表',
    'chronicle': '📜 纪要表',
}

TABLE_ORDER = [
    'global-state', 'protagonist-info', 'character-stats',
    'inventory', 'equipment', 'protagonist-skills', 'skills', 'quests',
    'npc-relations', 'factions', 'locations', 'memo', 'chronicle'
]

STATUS_COLORS = {
    '进行中': '#f59e0b',
    '已完成': '#10b981',
    '已失败': '#ef4444',
    '未开始': '#6b7280',
    '未归档': '#f59e0b',
    '已归档': '#10b981',
    '已废除': '#ef4444',
    '主线任务': '#8b5cf6',
    '支线任务': '#3b82f6',
    '是': '#10b981',
    '否': '#6b7280',
    '主动': '#8b5cf6',
    '被动': '#3b82f6',
    '在线': '#10b981',
    '离线': '#6b7280',
    '活着': '#10b981',
    '死亡': '#ef4444',
}

TABLE_ICONS = {
    'global-state': '🌍', 'protagonist-info': '👤', 'character-stats': '📊',
    'inventory': '🎒', 'quests': '📋', 'npc-relations': '🤝',
    'protagonist-skills': '⚡', 'skills': '⚡', 'equipment': '🛡️',
    'memo': '📝', 'factions': '🏰', 'locations': '📍', 'chronicle': '📜',
}


def load_db(db_name):
    """从 data 目录加载数据库 JSON"""
    db_path = os.path.join(DATA_DIR, f'{db_name}.json')
    if not os.path.exists(db_path):
        print(f'<!-- 数据库 "{db_name}" 不存在 -->')
        return None
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_all_tables(db_name):
    """获取所有表数据，按 TABLE_ORDER 排序"""
    db = load_db(db_name)
    if not db:
        return []
    tables = db.get('tables', {})
    ordered = []
    for tname in TABLE_ORDER:
        if tname in tables:
            ordered.append({
                'name': tname,
                'displayName': TABLE_DISPLAY_NAMES.get(tname, tname),
                'icon': TABLE_ICONS.get(tname, '📋'),
                'headers': tables[tname].get('headers', []),
                'rows': tables[tname].get('rows', []),
                'notes': tables[tname].get('notes', ''),
            })
    return ordered


def build_html(tables, db_name):
    """构建自包含 HTML"""
    safe_db_name = html_mod.escape(db_name)
    tables_json = json.dumps(tables, ensure_ascii=False)
    status_colors_json = json.dumps(STATUS_COLORS, ensure_ascii=False)
    table_count = len(tables)

    # 统计非空表数、总行数
    total_rows = sum(len(t['rows']) for t in tables)
    non_empty = sum(1 for t in tables if len(t['rows']) > 0)

    template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>游戏数据库 — __DB_NAME__</title>
<style>
:root {
  --bg: #0f172a;
  --bg-card: #1e293b;
  --bg-panel: linear-gradient(180deg, rgba(15,23,42,0.97) 0%, rgba(30,41,59,0.93) 100%);
  --border: rgba(56,189,248,0.5);
  --text: #f1f5f9;
  --text-sub: #94a3b8;
  --accent: #38bdf8;
  --accent2: #a855f7;
  --btn-bg: rgba(56,189,248,0.12);
  --btn-hover: rgba(56,189,248,0.22);
  --btn-active: linear-gradient(135deg, #38bdf8, #a855f7);
  --table-head: linear-gradient(90deg, rgba(56,189,248,0.08), rgba(168,85,247,0.08));
  --table-hover: rgba(56,189,248,0.06);
  --shadow: 0 8px 32px rgba(56,189,248,0.1);
  --badge: #334155;
  --radius: 10px;
  --font: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: var(--font);
  background: var(--bg-panel);
  color: var(--text);
  min-height: 100vh;
  padding: 16px;
  line-height: 1.5;
}
.header {
  text-align: center;
  padding: 20px 0 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}
.header h1 { font-size: 20px; background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.header .sub { font-size: 12px; color: var(--text-sub); margin-top: 4px; }
.header .sub .highlight { color: var(--accent); font-weight: 600; }
/* ── 顶部统计条 ── */
.top-stats {
  display: flex; gap: 12px; flex-wrap: wrap; justify-content: center;
  margin-bottom: 12px;
}
.top-stat {
  background: var(--bg-card); border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius); padding: 10px 18px; text-align: center;
  min-width: 80px;
}
.top-stat .num { font-size: 22px; font-weight: 700; color: var(--accent); }
.top-stat .label { font-size: 10px; color: var(--text-sub); margin-top: 2px; }
/* ── Tab 导航 ── */
.tabs {
  display: flex; flex-wrap: wrap; gap: 6px;
  padding: 12px 0; justify-content: center;
}
.tab {
  padding: 6px 14px; border-radius: 20px; font-size: 12px;
  background: var(--btn-bg); color: var(--text-sub);
  border: 1px solid transparent; cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.tab:hover { background: var(--btn-hover); color: var(--text); }
.tab.active { background: var(--btn-active); color: #fff; border-color: var(--accent); }
.tab.dashboard-tab {
  border-color: rgba(168,85,247,0.4);
  background: rgba(168,85,247,0.1);
}
.tab.dashboard-tab.active {
  background: linear-gradient(135deg, #a855f7, #7c3aed);
  border-color: #a855f7;
}
.tab .badge {
  display: inline-block; background: rgba(255,255,255,0.2);
  padding: 1px 7px; border-radius: 10px; font-size: 10px;
  margin-left: 4px;
}
/* ── 仪表盘 ── */
.dashboard { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.dash-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid rgba(255,255,255,0.06);
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow);
}
.dash-card:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 12px 40px rgba(56,189,248,0.18); }
.dash-card.empty { opacity: 0.4; cursor: default; }
.dash-card.empty:hover { border-color: rgba(255,255,255,0.06); transform: none; box-shadow: var(--shadow); }
.dash-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.dash-card-header .icon { font-size: 20px; }
.dash-card-header .title { font-size: 14px; font-weight: 600; color: var(--text); }
.dash-card-header .count { margin-left: auto; font-size: 11px; color: var(--text-sub); }
.dash-card-header .count strong { color: var(--accent); font-size: 16px; }
.dash-preview { font-size: 11px; color: var(--text-sub); line-height: 1.6; }
.dash-preview .row-preview {
  padding: 4px 8px; border-radius: 6px; background: rgba(255,255,255,0.03);
  margin-bottom: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.dash-preview .row-preview .kv { color: var(--text); }
.dash-preview .more { text-align: center; color: var(--accent); font-size: 10px; margin-top: 4px; }
.dash-empty { grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-sub); }
.dash-empty .icon { font-size: 48px; opacity: 0.3; margin-bottom: 8px; }
/* ── 面板 ── */
.panel { display: none; }
.panel.active { display: block; }
.card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(255,255,255,0.06);
  box-shadow: var(--shadow);
}
.card-title {
  font-size: 15px; font-weight: 600; margin-bottom: 12px;
  color: var(--accent);
}
.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th {
  background: var(--table-head);
  padding: 10px 12px; text-align: left;
  font-weight: 600; color: var(--text-sub);
  border-bottom: 2px solid var(--border);
  white-space: nowrap; font-size: 12px;
}
td {
  padding: 9px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: var(--text);
  max-width: 260px; overflow: hidden; text-overflow: ellipsis;
}
tr:hover td { background: var(--table-hover); }
.empty {
  text-align: center; padding: 40px 20px; color: var(--text-sub);
  font-size: 14px;
}
.empty-icon { font-size: 36px; margin-bottom: 8px; opacity: 0.5; }
.pagination {
  display: flex; justify-content: center; align-items: center;
  gap: 8px; margin-top: 12px; font-size: 12px;
}
.pagination button {
  padding: 4px 10px; border-radius: 6px;
  background: var(--btn-bg); color: var(--text-sub);
  border: 1px solid rgba(255,255,255,0.08); cursor: pointer;
  font-size: 12px;
}
.pagination button:hover { background: var(--btn-hover); color: var(--text); }
.pagination button:disabled { opacity: 0.4; cursor: default; }
.pagination span { color: var(--text-sub); }
.search-box {
  width: 100%; max-width: 300px; padding: 7px 12px;
  border-radius: 20px; border: 1px solid var(--border);
  background: rgba(255,255,255,0.05); color: var(--text);
  font-size: 12px; margin-bottom: 12px; outline: none;
  transition: border-color 0.2s;
}
.search-box:focus { border-color: var(--accent); }
.search-box::placeholder { color: var(--text-sub); }
.stats-row {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;
}
.stat-chip {
  padding: 4px 10px; border-radius: 14px; font-size: 11px;
  background: var(--badge); color: var(--text-sub);
}
@media (max-width: 640px) {
  body { padding: 8px; }
  .top-stats { gap: 6px; }
  .top-stat { padding: 8px 12px; min-width: 60px; }
  .top-stat .num { font-size: 18px; }
  .dashboard { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
  .tab { font-size: 11px; padding: 5px 10px; }
  .card { padding: 10px; }
  th, td { padding: 6px 8px; font-size: 11px; }
}
</style>
</head>
<body>
<div class="header">
  <h1>🎮 游戏数据库</h1>
  <div class="sub">数据库：<span class="highlight">__DB_NAME__</span></div>
</div>
<div class="top-stats">
  <div class="top-stat"><div class="num">__NONEMPTY__</div><div class="label">活跃表</div></div>
  <div class="top-stat"><div class="num">__TOTALROWS__</div><div class="label">总行数</div></div>
  <div class="top-stat"><div class="num">__TABLE_COUNT__</div><div class="label">全部表</div></div>
</div>
<div class="tabs" id="tabs"></div>
<div id="panels"></div>

<script>
var TABLES = __TABLES_JSON__;
var PER_PAGE = 15;
var activeTab = '__DASHBOARD__';

function getBadgeColor(val) {
  var map = __STATUS_COLORS__;
  return map[val] || null;
}

function esc(name) { return name.replace(/'/g, "\\\\'"); }

function renderTabs() {
  var container = document.getElementById('tabs');
  var nonEmpty = TABLES.filter(function(t) { return t.rows.length > 0; });
  var totalNonEmpty = nonEmpty.length;

  // Dashboard tab
  var dashActive = activeTab === '__DASHBOARD__';
  var html = '<div class="tab dashboard-tab' + (dashActive ? ' active' : '') + '" data-tab="__DASHBOARD__" onclick="showDashboard()">🏠 仪表盘<span class="badge">' + totalNonEmpty + '</span></div>';

  TABLES.forEach(function(t, i) {
    var emptyCls = t.rows.length === 0 ? ' style="opacity:0.5"' : '';
    var activeCls = activeTab === t.name;
    html += '<div class="tab' + (activeCls ? ' active' : '') + '" data-tab="' + t.name + '"' + emptyCls + ' onclick="showTab(\\'' + esc(t.name) + '\\')">' + t.displayName + '<span class="badge">' + t.rows.length + '</span></div>';
  });

  container.innerHTML = html;

  // Default to dashboard if no other active tab
  if (activeTab === '__DASHBOARD__') {
    showDashboard();
  }
}

function showDashboard() {
  activeTab = '__DASHBOARD__';
  document.querySelectorAll('.tab').forEach(function(el) {
    el.classList.toggle('active', el.getAttribute('data-tab') === '__DASHBOARD__');
  });

  var panels = document.getElementById('panels');
  var nonEmpty = TABLES.filter(function(t) { return t.rows.length > 0; });

  var html = '<div class="dashboard">';

  if (nonEmpty.length === 0) {
    html += '<div class="dash-empty"><div class="icon">📭</div><p>所有表暂无数据</p><p style="font-size:11px;margin-top:4px;">开始跑团后，数据将在此处汇总展示</p></div>';
  } else {
    nonEmpty.forEach(function(t) {
      html += '<div class="dash-card" onclick="showTab(\\'' + esc(t.name) + '\\')">';
      html += '<div class="dash-card-header">';
      html += '<span class="icon">' + (t.icon || '📋') + '</span>';
      html += '<span class="title">' + t.displayName + '</span>';
      html += '<span class="count"><strong>' + t.rows.length + '</strong> 行</span>';
      html += '</div>';
      html += '<div class="dash-preview">';

      // Show first 3 rows as preview
      var previewCount = Math.min(3, t.rows.length);
      for (var i = 0; i < previewCount; i++) {
        var rowPreview = '';
        // Pick first 2-3 meaningful columns
        var colsToShow = Math.min(3, t.headers.length);
        for (var j = 0; j < colsToShow; j++) {
          var val = t.rows[i][j] || '';
          if (val) {
            if (j > 0) rowPreview += ' · ';
            rowPreview += '<span class="kv">' + val + '</span>';
          }
        }
        html += '<div class="row-preview">' + rowPreview + '</div>';
      }

      if (t.rows.length > 3) {
        html += '<div class="more">还有 ' + (t.rows.length - 3) + ' 行... 点击查看 →</div>';
      }
      html += '</div></div>';
    });

    // Also show empty tables dimmed
    var empties = TABLES.filter(function(t) { return t.rows.length === 0; });
    empties.forEach(function(t) {
      html += '<div class="dash-card empty">';
      html += '<div class="dash-card-header">';
      html += '<span class="icon">' + (t.icon || '📋') + '</span>';
      html += '<span class="title">' + t.displayName + '</span>';
      html += '<span class="count">空</span>';
      html += '</div>';
      html += '<div class="dash-preview" style="text-align:center;padding:8px;">暂无数据</div>';
      html += '</div>';
    });
  }

  html += '</div>';
  panels.innerHTML = html;
}

function showTab(name) {
  activeTab = name;
  document.querySelectorAll('.tab').forEach(function(el) {
    el.classList.toggle('active', el.getAttribute('data-tab') === name);
  });
  var table = TABLES.find(function(t) { return t.name === name; });
  if (!table) return;
  var panels = document.getElementById('panels');

  var html = '<div class="card"><div class="card-title">' + table.displayName + '</div>';

  if (table.rows.length === 0) {
    html += '<div class="empty"><div class="empty-icon">📭</div>' + '暂无数据' + '</div>';
  } else {
    html += '<div class="stats-row"><div class="stat-chip">📋 ' + table.rows.length + ' 行</div><div class="stat-chip">📐 ' + table.headers.length + ' 列</div></div>';
    html += '<input class="search-box" placeholder="🔍 搜索..." oninput="filterTable(this.value)" id="search-' + name.replace(/'/g, '') + '">';
    html += '<div class="table-wrap"><table><thead><tr>';
    table.headers.forEach(function(h) {
      html += '<th>' + h + '</th>';
    });
    html += '</tr></thead><tbody id="tbody-' + name.replace(/'/g, '') + '">';
    renderRows(name, table.rows, 1);
    html += '</tbody></table></div>';

    var totalPages = Math.ceil(table.rows.length / PER_PAGE);
    if (totalPages > 1) {
      var safeName = name.replace(/'/g, "\\\\'");
      html += '<div class="pagination" id="pager-' + name.replace(/'/g, '') + '">';
      html += '<button onclick="goPage(\\'' + safeName + '\\', 0)" disabled>«</button>';
      html += '<button onclick="goPage(\\'' + safeName + '\\', -1)" disabled>‹</button>';
      html += '<span>第 <b>1</b> / ' + totalPages + ' 页</span>';
      html += '<button onclick="goPage(\\'' + safeName + '\\', 1)"' + (totalPages <= 1 ? ' disabled' : '') + '>›</button>';
      html += '<button onclick="goPage(\\'' + safeName + '\\', -2)"' + (totalPages <= 1 ? ' disabled' : '') + '>»</button>';
      html += '</div>';
    }
  }

  html += '</div>';
  panels.innerHTML = html;
  panels.dataset.currentTable = name;
  panels.dataset.currentPage = '1';
  panels.dataset.filtered = '';
}

function renderRows(tableName, rows, page) {
  var tbody = document.getElementById('tbody-' + tableName.replace(/'/g, ''));
  if (!tbody) return;
  var start = (page - 1) * PER_PAGE;
  var end = Math.min(start + PER_PAGE, rows.length);
  var table = TABLES.find(function(t) { return t.name === tableName; });
  var html = '';
  for (var i = start; i < end; i++) {
    html += '<tr>';
    table.headers.forEach(function(h, ci) {
      var val = rows[i][ci] || '';
      var color = getBadgeColor(val);
      var style = color ? ' style="color:' + color + ';font-weight:600"' : '';
      html += '<td' + style + '>' + val + '</td>';
    });
    html += '</tr>';
  }
  tbody.innerHTML = html;
}

var filteredRows = {};

function filterTable(query) {
  var panels = document.getElementById('panels');
  var name = panels.dataset.currentTable;
  var table = TABLES.find(function(t) { return t.name === name; });
  if (!table) return;
  var q = query.toLowerCase();
  panels.dataset.filtered = q;

  if (!q) {
    filteredRows[name] = null;
    renderRows(name, table.rows, 1);
    updatePager(name, table.rows.length);
    panels.dataset.currentPage = '1';
    return;
  }

  var filtered = table.rows.filter(function(row) {
    return row.some(function(cell) { return String(cell).toLowerCase().indexOf(q) !== -1; });
  });
  filteredRows[name] = filtered;
  renderRows(name, filtered, 1);
  updatePager(name, filtered.length);
  panels.dataset.currentPage = '1';
}

function goPage(tableName, direction) {
  var table = TABLES.find(function(t) { return t.name === tableName; });
  if (!table) return;
  var rows = filteredRows[tableName] || table.rows;
  var totalPages = Math.ceil(rows.length / PER_PAGE);
  var panels = document.getElementById('panels');
  var currentPage = parseInt(panels.dataset.currentPage || '1');

  if (direction === 0) currentPage = 1;
  else if (direction === -1) currentPage = Math.max(1, currentPage - 1);
  else if (direction === 1) currentPage = Math.min(totalPages, currentPage + 1);
  else if (direction === -2) currentPage = totalPages;

  panels.dataset.currentPage = String(currentPage);
  renderRows(tableName, rows, currentPage);
  updatePager(tableName, rows.length);
}

function updatePager(tableName, totalRows) {
  var pager = document.getElementById('pager-' + tableName.replace(/'/g, ''));
  if (!pager) return;
  var totalPages = Math.ceil(totalRows / PER_PAGE);
  var currentPage = parseInt(document.getElementById('panels').dataset.currentPage || '1');
  var safeName = tableName.replace(/'/g, "\\\\'");

  pager.innerHTML =
    '<button onclick="goPage(\\'' + safeName + '\\', 0)"' + (currentPage === 1 ? ' disabled' : '') + '>«</button>' +
    '<button onclick="goPage(\\'' + safeName + '\\', -1)"' + (currentPage === 1 ? ' disabled' : '') + '>‹</button>' +
    '<span>第 <b>' + currentPage + '</b> / ' + (totalPages || 1) + ' 页</span>' +
    '<button onclick="goPage(\\'' + safeName + '\\', 1)"' + (currentPage >= totalPages ? ' disabled' : '') + '>›</button>' +
    '<button onclick="goPage(\\'' + safeName + '\\', -2)"' + (currentPage >= totalPages ? ' disabled' : '') + '>»</button>';
}

// Init
renderTabs();
</script>
</body>
</html>'''

    html = template.replace('__DB_NAME__', safe_db_name)
    html = html.replace('__TABLE_COUNT__', str(table_count))
    html = html.replace('__TABLES_JSON__', tables_json)
    html = html.replace('__STATUS_COLORS__', status_colors_json)
    html = html.replace('__NONEMPTY__', str(non_empty))
    html = html.replace('__TOTALROWS__', str(total_rows))
    html = html.replace('__DASHBOARD__', '__DASHBOARD__')
    return html


def main():
    # Use UTF-8 encoding for stdout
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description='游戏数据库可视化前端')
    parser.add_argument('--db', default='default', help='数据库名称 (默认: default)')
    args = parser.parse_args()

    tables = get_all_tables(args.db)
    if not tables:
        print(f'<p style="color:#94a3b8;text-align:center;padding:40px;">📭 数据库 "{args.db}" 为空或不存在</p>')
        return

    html = build_html(tables, args.db)
    print(html)


if __name__ == '__main__':
    main()
