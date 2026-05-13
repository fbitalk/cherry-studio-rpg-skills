---
name: 世界书
description: "RPG / 跑团 / 角色扮演的世界设定管理。管理地理、历史、势力、NPC、魔法体系等固定世界观条目。通过关键词搜索匹配相关世界观信息，为 AI 角色扮演提供上下文。当用户提到世界观、世界设定、背景设定、世界书、lore、worldbook、构建世界、查询设定、记录设定、或任何需要创建/查询/整理游戏世界信息的场景时使用。与游戏数据库(rpg-database)紧密配合——世界书管静态设定，数据库管动态数据。"
---

# 世界书 Skill

## 与游戏数据库的关系

| 世界书 (worldbook) | 游戏数据库 (rpg-database) |
|---|---|
| **静态**：世界设定很少变化 | **动态**：角色数据随游戏变化 |
| 地点、人物、组织、历史、魔法... | 角色属性、背包物品、任务进度... |
| 条目式存储（key→content） | 表格存储（rows×columns） |
| 通过关键词搜索匹配 | 通过行列索引读写 |

游戏进行中，两个 skill 应同时参考：
1. 从世界书搜索相关世界观背景
2. 从数据库查看当前游戏状态
3. 综合两者生成符合世界观且数据一致的回复

## 快速参考

| 用户意图 | 命令 |
|----------|------|
| 创建世界书 | `python scripts/wb.py init <名称>` |
| 列出世界书 | `python scripts/wb.py list-wbs` |
| 创建条目 | `python scripts/wb.py create-entry <键名> --title "标题" --keywords "词1,词2" --category "分类" --content "内容" [--wb <世界书>]` |
| 查看条目 | `python scripts/wb.py get-entry <键名> [--wb <世界书>]` |
| 更新条目 | `python scripts/wb.py update-entry <键名> --title/content/keywords/category/order 新值 [--wb <世界书>]` |
| 删除条目 | `python scripts/wb.py delete-entry <键名> [--wb <世界书>]` |
| 列出条目 | `python scripts/wb.py list-entries [--wb <世界书>] [--category <分类>]` |
| 搜索条目 | `python scripts/wb.py search <查询词> [--wb <世界书>]` |
| 启用/禁用 | `python scripts/wb.py toggle-entry <键名> [--wb <世界书>]` |
| 概览 | `python scripts/wb.py summary [--wb <世界书>]` |
| 导出/导入 | `python scripts/wb.py export/import` |

## 初始化工作流

1. **创建世界书**：`python scripts/wb.py init my-world`
2. **按分类添加条目**（参考 `references/categories.md` 了解详细写作指南和模板）
3. **验证**：`python scripts/wb.py summary`

```bash
python scripts/wb.py init my-fantasy-world

# 添加地点
python scripts/wb.py create-entry stormwind --title "暴风城" --keywords "暴风城,Stormwind,人类都城,白城" --category "地点" --content "暴风城是人类最繁华的港口都城，白花岗岩城墙高耸。城内有贸易区、法师区、旧城区。狮鹫栖于城墙塔楼。" --order 20

# 添加人物
python scripts/wb.py create-entry king-anduin --title "安度因国王" --keywords "安度因,国王,乌瑞恩,Anduin" --category "人物" --content "安度因·乌瑞恩是暴风城的年轻国王。他崇尚和平外交，但也精通圣光法术和剑术。对冒险者持欢迎态度，经常委托公会处理王国事务。" --order 25

# 添加组织
python scripts/wb.py create-entry adventurers-guild --title "冒险者公会" --keywords "冒险者公会,公会,guild,任务板" --category "组织" --content "冒险者公会是横跨大陆的独立组织，提供任务中介、信息交换和基础补给。公会徽章是一把交叉的剑和羽毛笔。冒险者通过完成任务提升等级。" --order 20
```

## 搜索匹配（核心功能）

搜索是游戏进行中最常用的操作。当用户提到某个地名、人名、组织名时，搜索世界书获取相关上下文。

```bash
# 搜索单个词
python scripts/wb.py search "暴风城"

# 搜索英文关键词也有效
python scripts/wb.py search "Stormwind"

# JSON 格式输出（用于程序消费）
python scripts/wb.py search "艾尔文" --json
```

搜索逻辑：
- 在条目的 `title` 和 `keywords` 中进行子串匹配（不区分大小写）
- 按匹配度排序：精确匹配 > 前缀匹配 > 子串匹配
- 相同匹配度按 `order` 优先级降序排列
- 只返回已启用的条目

## 游戏进行中的工作流

当进行角色扮演/跑团时，每轮对话的工作流：

1. **理解用户消息**：提取关键词（地名、人名、物品名、组织名等）
2. **搜索世界书**：`python scripts/wb.py search "<关键词>"`
3. **查看数据库**：`python scripts/db.py summary` 或 `get-table`
4. **综合回复**：结合世界观背景和游戏数据，生成连贯的回复

示例对话流：

> 用户: "我来到冒险者公会，想接一个有悬赏的任务"

```bash
# Step 1: 搜索世界观
python scripts/wb.py search "冒险者公会"

# Step 2: 查看角色状态
python scripts/db.py get-table character-stats

# Step 3: 查看任务日志（看看有没有已有任务）
python scripts/db.py get-table quests

# Step 4: 综合以上信息回复用户
```

## 分类速查

| 分类 | 适用内容 | 优先级建议 |
|------|----------|------------|
| 地点 | 城市、建筑、地貌、地下城 | 10-20 |
| 人物 | NPC、历史人物、传说角色 | 20-30 |
| 组织 | 公会、王国、教派、商会 | 15-25 |
| 历史 | 战争、纪元、传说 | 5-15 |
| 魔法 | 法术体系、魔法物品 | 15-30 |
| 种族 | 精灵、矮人、兽人等 | 10-20 |
| 物品 | 神器、传说武器 | 20-40 |
| 地理 | 国家、大陆、地形地貌 | 10-20 |
| 力量体系 | 超自然能力、修炼等级 | 15-30 |
| 文化 | 货币、日历、法律、习俗 | 5-15 |
| 知识 | 技术、学术、秘传知识 | 10-20 |
| 其他 | 以上之外的杂项 | 5-15 |

完整的写作指南和条目模板，Read `references/categories.md`。

## 导入导出

```bash
# 导出备份
python scripts/wb.py export --wb my-world --file ~/backup-world.json

# 导入恢复
python scripts/wb.py import --file ~/backup-world.json --wb my-world --force
```

## 多世界管理

```bash
python scripts/wb.py init fantasy-world
python scripts/wb.py init scifi-world
python scripts/wb.py list-wbs
```

## 常见陷阱

1. **关键词太少**：一个条目最少要有 3-5 个关键词变体（中文、英文、昵称、简称）。
2. **内容过长**：每个条目的 content 控制在 2-5 句话，否则会挤占对话上下文。
3. **分类不明**：不确定分到哪类时选"其他"，之后再调整。
4. **忽略禁用**：暂时不用的条目用 `toggle-entry` 禁用，而不是删除。
5. **搜索词与关键词不匹配**：如果搜不到，试试用条目的部分名称或英文名。
6. **忘记检查世界书**：游戏进行中，每次回复前都应该 search 一下当前提到的地名/人名/物品。
