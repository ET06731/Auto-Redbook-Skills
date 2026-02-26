---
name: xhs-note-creator
description: 小红书笔记素材创作技能。当用户需要创建小红书笔记素材时使用这个技能。技能包含：根据用户的需求和提供的资料，撰写小红书笔记内容（标题+正文），生成图片卡片（封面+正文卡片），以及发布小红书笔记。
---

# 小红书笔记创作技能

这个技能用于创建专业的小红书笔记素材，包括内容撰写、图片卡片生成和笔记发布。

## 使用场景

- 用户需要创建小红书笔记时
- 用户提供资料需要转化为小红书风格内容时
- 用户需要生成精美的图片卡片用于发布时

## 工作流程

### 第一步：撰写小红书笔记正文内容

根据用户需求和提供的资料，创作符合小红书风格的内容：

#### 基础规范（所有场景通用）
- **标题**：不超过 20 字，传达内容核心。
- **正文排版**：使用良好的排版，段落清晰；使用简短的句子和段落，保存为md文件。
- **Tags标签**：结尾给出 SEO 友好的 Tags 标签（5-10 个相关标签）。
- **正文长度**：正文应包含 3-5 个有实质内容的段落，与卡片对应，避免泛泛而谈。


#### 风格指南（根据需求选择，默认执行【通用场景】）

**1. 通用场景（默认：适用于娱乐、效率神器、生活分享等）**
- **标题**：吸引眼球，制造好奇心。鼓励使用数字、疑问句、感叹号增强吸引力。示例：「5个让效率翻倍的神器推荐！」「震惊！原来这样做才对」。
- **正文**：需要适度活泼，点缀少量 Emoji 增加可读性（每段 1-2 个即可），语气可以更加感染人和带有互动性。

**2. 专业知识分享场景（适用于学术、专业科普等）**
- **标题**：准确描述内容，避免夸大词汇（避免使用"震惊""必看""绝绝子"等）。示例：「5款效率工具对比测评」「如何优雅地管理知识体系」。
- **正文**：客观陈述事实，内容客观严谨，避免绝对化表述，并视情况注明信息来源。
- **数据与支撑**：尽量提供具体数据或案例支撑，避免"效率翻倍""提升100%"等无法验证的夸大表述。
- **逻辑表达**：使用"推荐""可以尝试"等中性表达，而非"必须""不得不"等强制或主观推断。

### 第二步：生成 卡片Markdown 文档

**注意：这里生成的 Markdown 文档是用于渲染卡片的，必须专门生成，禁止直接使用上一步的笔记正文内容。**

Markdown 文件，文件应包含：

1. YAML 头部元数据（封面信息）：
```yaml
---
emoji: "🚀"           # 封面装饰 Emoji
title: "大标题"        # 封面大标题（不超过15字）
subtitle: "副标题文案"  # 封面副标题（不超过15字）
---
```

2. 用于渲染卡片的 Markdown 文本内容：
   - 当待渲染内容必须严格切分为独立的数张图片时，可使用 `---` 分割线主动将正文分隔为多个卡片段落（每个段落文本控制在 200 字左右），输出图片时使用参数`-m separator`
   - 当待渲染内容无需严格分割，生成正常 Markdown 文本即可，跟下方分页模式参数规则按需选择

完整 Markdown 文档内容示例：

```markdown
---
emoji: "💡"
title: "5个效率神器让工作效率翻倍"
subtitle: "对着抄作业就好了，一起变高效"
---

# 📝 神器一：Notion

> 全能型笔记工具，支持数据库、看板、日历等多种视图...

## 特色功能

- 特色一
- 特色二

# ⚡ 神器二：Raycast

\`\`\`
可使用代码块来增加渲染后图片的视觉丰富度
\`\`\`

## 推荐原因

- 原因一
- 原因二
- ……


# 🌈 神器三：Arc

全新理念的浏览器，侧边栏标签管理...

...

```

### 第三步：渲染图片卡片

将 Markdown 文档渲染为图片卡片。使用以下脚本渲染：

```bash
python scripts/render_xhs.py <markdown_file> [options]
```

- 默认输出目录为当前工作目录
- 生成的图片包括：封面（cover.png）和正文卡片（card_1.png, card_2.png, ...）

#### 渲染参数（Python）

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--output-dir` | `-o` | 输出目录 | 当前工作目录 |
| `--theme` | `-t` | 排版主题 | `default` |
| `--mode` | `-m` | 分页模式（推荐使用 `auto-fit`） | `separator` |
| `--width` | `-w` | 图片宽度 | `1080` |
| `--height` |  | 图片高度（`dynamic` 下为最小高度） | `1440` |
| `--max-height` |  | `dynamic` 最大高度 | `4320` |
| `--dpr` |  | 设备像素比（清晰度） | `2` |

#### 排版主题（`--theme`）

- `default`：默认简约浅灰渐变背景（`#f3f3f3 -> #f9f9f9`）
- `playful-geometric`：活泼几何（Memphis）
- `neo-brutalism`：新粗野主义
- `botanical`：植物园自然
- `professional`：专业商务
- `retro`：复古怀旧
- `terminal`：终端命令行
- `sketch`：手绘素描

#### 分页模式（`--mode`）

- `auto-fit`：**【推荐】** 固定尺寸下自动缩放文字，避免溢出/留白，无需手动控量。大多数场景首选。
- `auto-split`：按渲染后高度自动切分分页（适合切分不影响阅读的长文内容）
- `separator`：按 `---` 分隔符分页（适合需要精确控制每张卡片内容的情况）
- `dynamic`：根据内容动态调整图片高度（注意：图片最高 4320，字数超过 550 的不建使用此模式）

#### 文本溢出处理

当渲染后文字超出卡片边界时，按以下顺序尝试：

1. **自动缩放**：改用 `-m auto-fit`，渲染引擎会自动缩小字号直到内容填满画面不溢出。适合单张固定尺寸卡片。
2. **自动分页**：改用 `-m auto-split`，内容过长时自动拆成多张卡片，无需手动控量。
3. **手动拆分**：在 Markdown 中用 `---` 将内容切成更短的段落（每段建议 ≤200 字），再用 `-m separator` 渲染。这种方式对排版控制最精确。

#### 常用示例

```bash
# 1) 【推荐】自动缩放文字，固定 1080x1440，防溢出，大多数场景适用
python scripts/render_xhs.py content.md -m auto-fit

# 2) 自动切分分页（内容较长、段落较多时）
python scripts/render_xhs.py content.md -m auto-split

# 3) 手动分隔分页（需精确控制每张卡片内容时）
python scripts/render_xhs.py content.md -m separator

# 4) 动态高度（允许不固定高度）
python scripts/render_xhs.py content.md -m dynamic --max-height 4320

# 5) 切换主题（auto-fit 同样适用）
python scripts/render_xhs.py content.md -t playful-geometric -m auto-fit
```

#### Node.js 渲染（可选）

```bash
node scripts/render_xhs.js content.md -t default -m separator
```

Node.js 参数与 Python 基本一致：`--output-dir/-o`、`--theme/-t`、`--mode/-m`、`--width/-w`、`--height`、`--max-height`、`--dpr`。

### 第四步：发布小红书笔记（可选）

使用发布脚本将生成的图片发布到小红书：

```bash
# 通过 md 文件传入正文（推荐）
python scripts/publish_xhs.py --title "笔记标题" --desc-file note.md --images card_1.png card_2.png cover.png

# 直接传入正文文本
python scripts/publish_xhs.py --title "笔记标题" --desc "笔记描述" --images card_1.png card_2.png cover.png
```

| 参数 | 简写 | 说明 |
|---|---|---|
| `--title` | `-t` | 笔记标题 |
| `--desc` | `-d` | 正文文本（与 `--desc-file` 二选一） |
| `--desc-file` | `-f` | 从 Markdown 文件读取正文，优先于 `--desc` |
| `--images` | `-i` | 图片路径（可多个） |
| `--private` |  | 设为私密笔记 |
| `--post-time` |  | 定时发布，格式 `2024-01-01 12:00:00` |

**前置条件**：

1. 需配置小红书 Cookie：
```
XHS_COOKIE=your_cookie_string_here
```

2. Cookie 获取方式：
   - 在浏览器中登录小红书（https://www.xiaohongshu.com）
   - 打开开发者工具（F12）
   - 在 Network 标签中查看请求头的 Cookie

## 图片规格说明

### 封面卡片
- 尺寸比例：3:4（小红书推荐比例）
- 基准尺寸：1080×1440px
- 包含：Emoji 装饰、大标题、副标题
- 样式：渐变背景 + 圆角内容区

### 正文卡片
- 尺寸比例：3:4
- 基准尺寸：1080×1440px
- 支持：标题、段落、列表、引用、代码块、图片
- 样式：白色卡片 + 渐变背景边框

## 技能资源

### 脚本文件
- `scripts/render_xhs.py` - Python 渲染脚本
- `scripts/render_xhs.js` - Node.js 渲染脚本
- `scripts/publish_xhs.py` - 小红书发布脚本

### 资源文件
- `assets/cover.html` - 封面 HTML 模板
- `assets/card.html` - 正文卡片 HTML 模板
- `assets/styles.css` - 共用样式表

## 注意事项

1. Markdown 文件应保存在工作目录，渲染后的图片也保存在工作目录
2. 技能目录 (`md2Redbook/`) 仅存放脚本和模板，不存放用户数据
3. 图片尺寸会根据内容自动调整，但保持 3:4 比例
4. Cookie 有有效期限制，过期后需要重新获取
5. 发布功能依赖 xhs 库，需要安装：`pip install xhs`
6. 用uv进行Python环境管理
