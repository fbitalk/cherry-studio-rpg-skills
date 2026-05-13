---
name: 游戏数据库
description: "RPG / 跑团 / 角色扮演游戏的结构化数据库。管理全局状态、主角信息、角色属性、背包物品、任务日志、角色关系、技能、装备、备忘录、势力、地点、纪要等12类表格数据。支持创建多表格、增删改查、JSON导入导出。当用户提到角色卡、人物属性、背包、任务列表、NPC好感度、跑团数据、记录一下、帮我登记、更新数据或任何需要结构化跟踪游戏数据的场景时使用。与世界书(worldbook)配合——数据库管动态数据，世界书管静态设定。也适用于非游戏场景的表格数据追踪。"
---

# 游戏数据库 Skill

## ⚠️ 强制规则：每次回复必须附带可视化卡片

**当此 skill 被触发后，在每次回复末尾必须运行以下命令并附加其输出：**

```bash
python scripts/viz.py --db <当前数据库名>
```

**将输出作为 ` ```html ` 代码块附在回复的最后。** 这条规则适用于：
- 查询数据后
- 插入/更新/删除数据后
- 初始化数据库/创建表格后
- AI 驱动数据更新后
- 世界书联动回复后

唯一例外：纯文本咨询（如 "这个命令怎么用？"），不涉及具体数据操作时可不附加。

> Cherry Studio 的 `HtmlArtifactsCard` 组件会自动将 HTML 代码块渲染为交互式可视化卡片。

---

## 快速参考

| 用户意图 | 命令 |
|----------|------|
| 创建新数据库 | `python scripts/db.py init <名称>` |
| 列出数据库 | `python scripts/db.py list-dbs` |
| 创建表格 | `python scripts/db.py create-table <键名> --headers "列1,列2,列3" [--db <库名>] [--notes "备注"]` |
| 列出表格 | `python scripts/db.py list-tables [--db <库名>]` |
| 查看表格 | `python scripts/db.py get-table <键名> [--db <库名>] [--json] [--last N] [--columns "列1,列2"] [--where "列=值1,值2"]` |
| 更新单元格 | `python scripts/db.py update-cell <表> <行> <列> <值> [--db <库名>]` |
| 更新整行 | `python scripts/db.py update-row <表> <行> --data '{"列":"值",...}' [--db <库名>]` |
| 插入行 | `python scripts/db.py insert-row <表> --data '{"列":"值",...}' [--db <库名>]` |
| 删除行 | `python scripts/db.py delete-row <表> <行> [--db <库名>]` |
| 删除表格 | `python scripts/db.py delete-table <键名> [--db <库名>]` |
| 检查Token | `python scripts/db.py check-tokens [--db <库名>]` |
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

## 操作权限速查

**核心原则：数据不丢、归档锁定、追加优于修改。**

| 表格 | 插入 | 更新 | 删除 |
|------|:--:|:--:|:--:|
| global-state | ❌ 禁止 | ✅ 换地/换时 | ❌ 禁止 |
| protagonist-info | ❌ 禁止 | ✅ 换装/重大改变 | ❌ 禁止 |
| character-stats | ✅ 新属性 | ✅ 数值变化 | ✅ 属性被剥夺 |
| inventory | ✅ 新物品 | ✅ 数量/状态变化 | ✅ 归零/丢弃 |
| quests | ✅ 新任务 | ✅ 进度/状态变化 | ⚠️ 极少 |
| npc-relations | ✅ 新NPC登场 | ✅ 状态/关系/好感 | ❌ 禁止 |
| protagonist-skills | ✅ 新技能 | ✅ 升级 | ✅ 被剥夺 |
| equipment | ✅ 新装备 | ✅ 耐久/强化 | ✅ 损毁 |
| memo | ⚠️ 仅事件闭环 | ⚠️ 仅未归档状态 | ❌ 禁止 |
| factions | ✅ 新势力 | ✅ 领袖/关系变 | ✅ 覆灭 |
| locations | ✅ 新地点 | ✅ 现状变化 | ✅ 彻底消失 |
| chronicle | ✅ 每轮追加 | ❌ 禁止 | ❌ 禁止 |

详细规则见 `references/templates.md`。

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
| `protagonist-skills` | 主角技能 | 技能名称, 技能类型, 等级/阶段, 消耗, 效果描述 |
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

**每次数据库操作后，必须在回复末尾附带可视化 HTML 卡片。**

### 使用方式

```bash
python scripts/viz.py --db <数据库名>
```

将 stdout 输出完整复制，作为 ` ```html ` 代码块附在回复末尾。Cherry Studio 的 `HtmlArtifactsCard` 组件会自动渲染。

### 操作后检查清单

每次完成数据库操作后，按以下步骤确保可视化被附带：

1. ✅ 执行数据库操作（增删改查）
2. ✅ 运行 `python scripts/viz.py --db <数据库名>`
3. ✅ 将 HTML 输出粘贴到回复末尾的 ` ```html ` 代码块中

### 示例

````markdown
# 你的文字回复...

已更新角色属性：生命值 100 → 80。

```html
<!-- viz.py 的输出粘贴在这里 -->
```
````

### 可视化功能

- 🏠 **仪表盘标签** — 首个标签展示所有非空表的概览统计
- 📑 **Tab 页签** — 12 个表以 Tab 切换，含行数角标
- 🎨 **状态着色** — 进行中=橙、已完成=绿、已失败=红、未开始=灰…
- 🔍 **实时搜索** — 输入即过滤当前表数据
- 📄 **自动分页** — 超过 15 行自动分页，支持首/末/前/后翻页
- 📱 **响应式** — 适配桌面和移动端
- 💫 **深色主题** — 游戏风格的蓝紫渐变暗色 UI

## 日常操作

### 查看数据

```bash
# 人类可读格式（默认）
python scripts/db.py get-table character-stats

# JSON 格式（程序化消费）
python scripts/db.py get-table character-stats --json

# 只看最后5轮纪要
python scripts/db.py get-table chronicle --last 5

# 只看索引（不拉全文）
python scripts/db.py get-table chronicle --columns "概览,编码索引"

# 按条件过滤（Recall 用）
python scripts/db.py get-table chronicle --where "编码索引=AM012,AM007,AM019" --json

# 组合过滤 + 投影
python scripts/db.py get-table npc-relations --where "是否在场=是" --columns "姓名,好感度,身份"
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

⚠️ **更新备忘录前检查归档状态**：已归档/已废除的备忘录禁止修改。先用 `get-table` 确认归档状态为"未归档"后再执行更新。

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
python ../worldbook/scripts/wb.py search "冒险者公会" --wb my-world

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

## Token 管理

在大上下文场景中，部分表格可能消耗大量 Token。AI 应在更新关键经历、纪要等大文本字段前估算 Token。

### 检查总 Token 占用

```bash
# 检查整个数据库的 Token 估算
python scripts/db.py check-tokens --db <数据库名>
```

输出示例：
```
表 "npc-relations" — 关键经历: ~85 tokens (上限 300) ✅
表 "npc-relations" — 背景故事: ~42 tokens (上限 150) ✅
表 "memo" — 记录内容: ~120 tokens (上限 300) ✅
表 "chronicle" — 纪要: ~560 tokens (无硬上限，建议关注)
```

### Token 估算规则

- 中文字符：1 字符 ≈ 0.5 token
- 英文单词：1 词 ≈ 1 token
- 粗略公式：`总 Token ≈ 中文字符数 × 0.5 + 英文词数`

### 压缩策略

当 npc-relations 的关键经历列接近 300 token 上限时：
1. 找出最早且内容最相近的 2-3 条经历
2. 合并为 1 条（≤ 30 token），删除原条目
3. 保持总 token ≤ 300

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
