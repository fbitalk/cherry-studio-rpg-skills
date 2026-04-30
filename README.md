# Cherry Studio RPG Skills

Cherry Studio 角色扮演游戏专用 skills 组合：世界书（静态设定）+ 数据库（动态数据）。

## 📦 包含 Skill

### 🌍 世界书 (worldbook)
管理 RPG 世界观的固定设定 —— 地理、历史、势力、NPC、魔法体系等。通过关键词搜索匹配上下文，为 AI 角色扮演提供世界背景。

- **8 大分类**: 地点、人物、组织、历史、魔法、种族、物品、其他
- **核心功能**: 关键词搜索（精确 > 前缀 > 子串匹配）、增删改查、启用/禁用条目
- **脚本**: `python scripts/wb.py <命令> [参数]`

### 🎮 游戏数据库 (rpg-database)
管理 RPG 游戏进程中的动态数据 —— 角色状态、物品、任务、关系等结构化表格。

- **12 类数据表**: 全局状态、主角信息、角色属性、背包、任务、NPC关系、技能、装备、备忘录、势力、地点、纪要
- **核心功能**: 表格级增删改查、JSON 导入导出、内容摘要
- **脚本**: `python scripts/db.py <命令> [参数]`
- **可视化**: 支持输出 HTML 卡片（Cherry Studio `HtmlArtifactsCard` 渲染）

## 🔗 两者配合

| 世界书 | 游戏数据库 |
|--------|-----------|
| 静态世界观设定 | 动态游戏数据 |
| 运行时查询参考 | 实时增删改查 |
| 提供叙事上下文 | 追踪进度状态 |

## 🚀 安装

### 前置条件
- Python 3.7+（仅标准库，无第三方依赖）
- **重要**: 两个 skill 的 `scripts/` 和 `references/` 配置在 skill YAML frontmatter 中，需要放置在 Cherry Studio 的 Skills 目录下

### 安装到 Cherry Studio

**方式一：通过 Skill 管理界面**
1. 在 Cherry Studio 中打开设置 → Skills
2. 点击「安装 Skill」
3. 输入本仓库的 GitHub URL

**方式二：手动安装**
1. 将本仓库克隆到 Cherry Studio 的 Skills 目录：
   ```
   %APPDATA%\CherryStudio\Data\Skills\
   ```
2. 确保目录结构为：
   ```
   <Skills目录>/
     rpg-database/
       SKILL.md
       scripts/db.py, viz.py
       references/templates.md
     worldbook/
       SKILL.md
       scripts/wb.py
       references/categories.md
   ```

## 📖 使用示例

```
用户: 创建一个「修仙世界」的世界书，设定几个主要门派

Agent: [调用 worldbook skill 创建条目]

用户: 初始化游戏数据库，主角叫林风

Agent: [调用 rpg-database skill 初始化数据库和主角]

用户: 林风前往青云宗拜师学艺

Agent: [查世界书确认青云宗设定 → 查数据库确认林风状态 → 叙事 → 更新数据库]
```

## 📂 目录结构

```
cherry-studio-rpg-skills/
├── rpg-database/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── db.py          # 数据库 CLI
│   │   └── viz.py         # HTML 可视化
│   └── references/
│       └── templates.md   # 12类表格模板
├── worldbook/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── wb.py          # 世界书 CLI
│   └── references/
│       └── categories.md  # 8类条目模板
├── 小说之神-提示词.md      # 配套智能体提示词
└── README.md
```

## 📄 许可证

MIT
