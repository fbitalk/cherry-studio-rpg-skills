---
name: 游戏数据库
description: "RPG / 跑团 / 角色扮演游戏的结构化数据库。管理全局状态、主角信息、角色属性、背包物品、任务日志、角色关系、技能、装备、备忘录、势力、地点、纪要等12类表格数据。支持创建多表格、增删改查、JSON导入导出。当用户提到角色卡、人物属性、背包、任务列表、NPC好感度、跑团数据、记录一下、帮我登记、更新数据或任何需要结构化跟踪游戏数据的场景时使用。与世界书(worldbook)配合——数据库管动态数据，世界书管静态设定。也适用于非游戏场景的表格数据追踪。"
---

# 游戏数据库 Skill

## 快速参考

| 用户意图 | 命令 |
|----------|------|
| 创建新数据库 | `python scripts/db.py init <名称>` |
| 列出数据库 | `python scripts/db.py list-dbs` |
| 创建表格 | `python scripts/db.py create-table <键名> --headers "列1,列2,列3" [--db <库名>] [--notes "备注"]` |
| 列出表格 | `python scripts/db.py list-tables [--db <库名>]` |
| 查看表格 | `python scripts/db.py get-table <键名> [--db <库名>]` |
| 更新单元格 | `python scripts/db.py update-cell <表> <行> <列> <值> [--db <库名>]` |
| 更新整行 | `python scripts/db.py update-row <表> <行> --data '{"列":"值",...}' [--db <库名>]` |
| 插入行 | `python scripts/db.py insert-row <表> --data '{"列":"值",...}' [--db <库名>]` |
| 删除行 | `python scripts/db.py delete-row <表> <行> [--db <库名>]` |
| 删除表格 | `python scripts/db.py delete-table <键名> [--db <库名>]` |
| 概览 | `python scripts/db.py summary [--db <库名>]` |
| 导出 | `python scripts/db.py export [--db <库名>] [--file <路径>]` |
| 导入 | `python scripts/db.py import --file <路径> [--db <库名>]` |

默认数据库名为 `default`，无需每次指定 `--db`。管理多个战役/会话时才用 `--db`。

## 初始化工作流

首次使用时，按以下步骤操作：

1. **创建数据库**：`python scripts/db.py init <名称>`
2. **创建表格**：根据场景从模板中选择（见下方模板速查）
3. **填充数据**：用 `insert-row` 添加初始数据

示例：
```bash
python scripts/db.py init my-campaign
python scripts/db.py create-table character-stats --headers "角色名,属性名,当前值,最大值,备注"
python scripts/db.py insert-row character-stats --data '{"角色名":"艾伦","属性名":"生命值","当前值":"100","最大值":"100","备注":""}'
```

## 模板速查

所有模板详见 `references/templates.md`。快速一览：

| 模板键 | 中文名 | 列头 |
|--------|--------|------|
| `global-state` | 全局状态 | 角色名, 当前地点, 当前时间, 上轮时间, 经过时间, 备注 |
| `protagonist-info` | 主角信息 | 角色名, 性别/年龄, 外貌特征, 当前衣着, 职业/身份, 备注 |
| `character-stats` | 角色属性 | 角色名, 属性名, 当前值, 最大值, 备注 |
| `inventory` | 背包物品 | 物品名称, 数量, 类别, 归属, 描述, 备注 |
| `quests` | 任务日志 | 任务名称, 任务类型, 状态, 发布者, 详细描述, 当前进度, 任务时限, 奖励, 惩罚 |
| `npc-relations` | 角色关系 | 姓名, 性别/年龄, 外貌特征, 当前衣着, 身份/职业, 好感度, 是否在场, 背景故事, 关键经历, 人际关系, 简介, 别称, 备注 |
| `skills` | 技能列表 | 技能名称, 技能类型, 等级, 消耗, 效果描述 |
| `equipment` | 装备栏 | 装备名, 部位, 属性加成, 耐久度, 归属, 描述 |
| `memo` | 备忘录 | 标题, 分类, 归档状态, 记录日期, 记录内容, 涉及对象, 关键要素 |
| `factions` | 势力表 | 名称, 描述, 领袖, 关系, 位置 |
| `locations` | 地点表 | 地点名称, 所属区域, 地点描述, 地点现状 |
| `chronicle` | 纪要表 | 时间跨度, 地点, 纪要, 概览, 编码索引 |

创建模板表格：
```bash
python scripts/db.py create-table inventory --headers "物品名称,数量,类别,归属,描述,备注"
# 参考 references/templates.md 获取每个模板的完整说明和示例数据
```

需要模板的完整说明时，Read `references/templates.md`。

## 可视化前端

每次涉及数据库数据展示时（查询、初始化、数据变更后确认），必须在回复末尾附上可视化卡片。

### 使用方法

```bash
python scripts/viz.py [--db <数据库名>]
```

该命令输出自包含 HTML，Cherry Studio 的 `HtmlArtifactsCard` 组件会自动渲染为可视化卡片。

**工作流：**
1. 执行数据库操作（增删改查）
2. 运行 `python scripts/viz.py --db <数据库名>` 生成 HTML
3. 将 HTML 输出作为 ````html` 代码块附在回复末尾
4. 可视化卡片自动展示所有表数据：Tab 切换、搜索过滤、分页、状态着色

**示例：**
```bash
# 查看数据库后附上可视化
python scripts/db.py get-table character-stats --db my-campaign
python scripts/viz.py --db my-campaign
```

**效果：**
- 12 个表以 Tab 页签切换
- 数据行按状态自动着色（进行中=橙、已完成=绿、已失败=红…）
- 支持搜索框实时过滤
- 超过 15 行自动分页
- 空表显示占位提示
- 响应式布局，适配移动端

> **注意**：仅在涉及数据查看/变更的回复中附加可视化卡片。纯咨询、纯文本操作等无需可视化。

## 日常操作

### 查看数据

```bash
# 人类可读格式（默认）
python scripts/db.py get-table character-stats

# JSON 格式（程序化消费）
python scripts/db.py get-table character-stats --json
```

### 更新数据

```bash
# 更新单个单元格（修改生命值）
python scripts/db.py update-cell character-stats 0 当前值 75

# 更新整行（多个字段一起改）
python scripts/db.py update-row character-stats 0 --data '{"当前值":"80","最大值":"120"}'

# 修改背包物品数量
python scripts/db.py update-cell inventory 0 数量 2
```

### 添加数据

```bash
# 添加任务
python scripts/db.py insert-row quests --data '{"任务名称":"寻找魔法水晶","任务类型":"主线任务","状态":"未开始","发布者":"法师塔","详细描述":"深入地下城取回魔法水晶","当前进度":"无","任务时限":"无","奖励":"魔法戒指","惩罚":"无"}'

# 添加 NPC 关系
python scripts/db.py insert-row npc-relations --data '{"姓名":"老铁匠","性别/年龄":"男/58","外貌特征":"灰白短发，健壮","当前衣着":"皮围裙","身份/职业":"武器店老板","好感度":"30","是否在场":"是","背景故事":"1.经营武器店三十年","关键经历":"1.卖给主角一把铁剑","人际关系":"主角:买卖关系","简介":"镇上唯一的铁匠","别称":"老铁","备注":""}'

# 添加物品
python scripts/db.py insert-row inventory --data '{"物品名称":"法力药水","数量":"2","类别":"消耗品","归属":"艾伦","描述":"恢复30点法力值","备注":""}'
```

### 删除数据

```bash
# 删除某行（完成任务后移除）
python scripts/db.py delete-row quests 2

# 删除最后一行
python scripts/db.py delete-row inventory last
```

## 世界书联动

当进行角色扮演/跑团游戏时，应与世界书 (worldbook) skill 配合使用：

| Skill | 管什么 | 数据特性 |
|-------|--------|----------|
| worldbook (世界书) | 固定世界观设定 | 静态，很少变化 |
| rpg-database (数据库) | 动态游戏数据 | 随游戏进程变化 |

**游戏对话中的工作流：**

每次回复前按顺序执行：

1. **搜索世界书**：从用户消息中提取关键词（地名、人名、物品名），查找相关世界观条目
2. **查看数据库**：获取当前游戏状态（角色属性、背包、任务等）
3. **综合回复**：结合世界观背景 + 游戏数据 + 用户消息，生成连贯的回复

示例：
```bash
# 用户: "我来到冒险者公会，想接一个悬赏任务"

# 1. 搜索世界观
python scripts/wb.py search "冒险者公会" --wb my-world

# 2. 查看角色状态
python scripts/db.py get-table character-stats --json

# 3. 查看已有任务
python scripts/db.py get-table quests --json

# 4. 综合以上信息，描述公会场景，提供可选任务，更新任务表
```

## AI 驱动数据更新

当用户在对话中描述游戏进展时，主动分析并执行对应的数据库操作。

**工作流程：**
1. 先 `get-table <表名>` 查看当前状态
2. 根据用户描述判断需要什么操作
3. 执行相应命令（update-cell / insert-row / delete-row）
4. 告知用户变更结果

**示例：**

| 用户说 | 操作 |
|--------|------|
| "我喝了治疗药水" | 查看 inventory 找到治疗药水行，数量减 1 |
| "村长给我一个新任务" | insert-row quests |
| "升级了，力量+2" | update-cell character-stats <行> 当前值 18 |
| "和铁匠关系变好了" | update-cell npc-relations <行> 好感度 <新值> |
| "铁剑坏了不能用了" | update-cell equipment <行> 耐久度 0 |
| "任务完成了" | update-cell quests <行> 状态 已完成 |
| "抵达了新城市" | update-cell global-state 0 当前地点 <新地点> |
| "发现了重要线索" | insert-row memo |
| "轮次结束" | insert-row chronicle |

## 导入导出

```bash
# 导出备份
python scripts/db.py export --db my-campaign --file ~/backup-campaign.json

# 导入恢复
python scripts/db.py import --file ~/backup-campaign.json --db my-campaign --force

# 默认导出到 data/ 目录
python scripts/db.py export
```

## 多数据库

用 `--db` 管理独立的数据库（战役/会话/故事线）：

```bash
python scripts/db.py init campaign-fantasy
python scripts/db.py init campaign-scifi
python scripts/db.py list-dbs
python scripts/db.py summary --db campaign-fantasy
```

## 常见陷阱

1. **行索引从 0 开始**，不是 1。用 `last` 表示最后一行。
2. **列名区分大小写**，必须与创建表格时的列头完全一致。
3. **列头中的分隔符**：列头使用半角逗号分隔。如果列头本身需要逗号，用中文逗号 `，`。
4. **值中的空格**：如果值包含空格或特殊字符，确保在 shell 中正确引用。
5. **`--data` 必须是有效 JSON**：键和字符串值用双引号，数字不需要引号。
6. **修改数据前先查看**：用 `get-table` 确认当前状态和目标行索引。
7. **并行操作**：同一数据库的多个操作不要并行执行，按顺序操作避免数据竞争。
