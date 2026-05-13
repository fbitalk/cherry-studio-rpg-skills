# 🎲 Cherry Studio RPG Skills

> 为 Cherry Studio 打造的角色扮演游戏增强技能包 —— 世界书管理静态设定，数据库追踪动态数据，让 AI 成为专业 GM。

[![Skills](https://img.shields.io/badge/Cherry_Studio-Skills-7B68EE)](https://cherry-ai.com)
[![Python](https://img.shields.io/badge/Python-3.7+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Win|Mac|Linux-lightgrey)]()

---

## 这是什么

两个互相配合的 Cherry Studio Agent Skill，专为文字角色扮演游戏（跑团 / TRPG / 互动叙事）设计：

| Skill | 职责 | 数据特性 |
|-------|------|----------|
| 🌍 **世界书** | 世界观设定（地理、历史、人物、魔法体系…） | 静态，偶尔修订 |
| 🎮 **游戏数据库** | 游戏进程数据（角色状态、背包、任务、关系…） | 动态，每轮更新 |

AI 在对话中同时查阅两者 —— 世界书提供故事背景，数据库提供当前状态 —— 让角色扮演不再"失忆"。

---

## 能力一览

### 🌍 世界书

- **12 大分类**：地点、人物、组织、历史、魔法、种族、物品、地理、力量体系、文化、知识、其他
- **智能搜索**：精确匹配 > 前缀匹配 > 子串匹配，中英文关键词通吃
- **条目管理**：增删改查、启用/禁用、优先级排序
- **多世界并存**：同时管理奇幻、科幻、克苏鲁等多个世界观
- **JSON 导入导出**：备份恢复一键搞定

### 🎮 游戏数据库

- **12 类数据表**：全局状态、主角信息、角色属性、背包、任务、NPC关系、技能、装备、备忘录、势力、地点、纪要
- **完整 CRUD**：单元格/行/表三级操作，权限分级（有些表禁止删除）
- **AI 自动感知**：描述"喝了药水"→自动扣减背包数量
- **HTML 可视化卡片**：Cherry Studio 原生渲染，Tab 切换、实时搜索、分页浏览
- **Token 估算**：长文本字段压缩提醒，适应大上下文场景
- **多战役管理**：`--db` 切换独立的游戏存档

### 🔗 协同工作流

```
用户消息 → 提取关键词 → 搜索世界书 → 查看数据库 → 综合生成回复 → 更新数据库 → 渲染可视化卡片
```

---

## 快速开始

### 安装

**方式一：Cherry Studio 界面安装（推荐）**

1. 打开 Cherry Studio → 设置 → Skills
2. 点击「安装 Skill」
3. 输入仓库地址：`https://github.com/fbitalk/cherry-studio-rpg-skills`

**方式二：手动安装**

```bash
cd "%APPDATA%\CherryStudio\Data\Skills"
git clone https://github.com/fbitalk/cherry-studio-rpg-skills.git
```

### 首次使用

```
# 在世界书的 Agent 对话中：
创建一个「修仙世界」，设定三个主要门派

# 在数据库的 Agent 对话中：
初始化游戏数据库，主角叫林风，是一名散修
```

---

## 使用示例

```
👤 用户：林风前往青云宗，想拜入山门

🤖 Agent：
  [搜索世界书: "青云宗"] → 青云宗是正道第一剑修门派，山门设有问心剑阵…
  [查询数据库: 林风状态] → 林风，练气三层，散修，无门派
  [生成回复] → 林风来到青云山脚下，巍峨的山门隐于云雾之中。
               守门弟子拦住去路："来者何人？"
               …
  [更新数据库] → 插入新任务「入门试炼」
  [渲染卡片]   → 当前状态一览
```

---

## 与普通 AI 跑团的区别

| | 普通聊天 | 使用本 Skill |
|---|---|---|
| 世界观一致性 | 容易前后矛盾 | 自动检索并贴合设定 |
| 数据追踪 | 靠记忆/手动笔记 | 结构化存储、即时查询 |
| 上下文长度 | 越聊越超 token | 只注入相关条目 |
| 视觉反馈 | 纯文字 | HTML 可视化卡片 |
| 多战役切换 | 混乱 | 独立存档一键切换 |

---

## 目录结构

```
cherry-studio-rpg-skills/
├── rpg-database/              # 游戏数据库 Skill
│   ├── SKILL.md               # Skill 定义（Agent 指令）
│   ├── scripts/
│   │   ├── db.py              # 数据库 CLI（12 表 CRUD）
│   │   └── viz.py             # HTML 可视化卡片生成器
│   └── references/
│       └── templates.md       # 12 类表格模板与权限规则
├── worldbook/                 # 世界书 Skill
│   ├── SKILL.md               # Skill 定义（Agent 指令）
│   ├── scripts/
│   │   └── wb.py              # 世界书 CLI（条目管理 + 搜索）
│   └── references/
│       └── categories.md      # 12 类条目写作指南
├── 小说之神-提示词.md          # 配套智能体 System Prompt
└── README.md
```

---

## 依赖

- **Python 3.7+**（纯标准库，零 pip 依赖）
- **Cherry Studio** ≥ 1.0（需支持 Agent Skills 和 `HtmlArtifactsCard`）

---

## 配套提示词

仓库中的 `游戏之神-提示词.md` 是一个完整的智能体 System Prompt，可直接用于创建「小说之神」Agent，配合两个 Skill 实现沉浸式互动叙事。

---

## 贡献与反馈

- 🐛 遇到问题？[提交 Issue](https://github.com/fbitalk/cherry-studio-rpg-skills/issues)
- 💡 有建议？欢迎 PR 或在 Discussions 讨论
- 📖 更多 Cherry Studio Skills：[Cherry Studio 文档](https://docs.cherry-ai.com)

---

## 许可证

MIT
