# AGENTS.md

## 我是谁

`Win11Debloat-skill-zh` 告诉你怎么把 Win11Debloat 英文原版的 Config JSON 文件完整翻译成简体中文。你的任务就是读 `SKILL.md` 的规则，对着英文原版，把中文翻出来。

不管你是 Cursor、Cline、ChatGPT、Claude、还是别的什么 AI，流程都一样。

## 第零步：先搞清楚目录结构

用户的工作目录长这样（名字可能不同，但结构不变）：

```
<工作目录>/
├── Win11Debloat-skill-zh/  # 本项目，SKILL.md 在这里
│   ├── SKILL.md       # 翻译规则（你先读完这个）
│   ├── AGENTS.md      # ← 你在读的这个文件
│   └── README.md
└── Win11Debloat/      # 英文原版（第三方的，别改）
    └── Config/
        ├── Features.json   ← 核心翻译目标
        ├── Apps.json       ← 应用列表翻译
        └── DefaultSettings.json  ← 不用翻，但要保证 BOM
```

如果目录结构不对，先问用户："Win11Debloat 英文原版在哪？"

## 收到"翻译"指令后，严格按这 5 步走

### 步骤 1：确认源文件

检查 `Win11Debloat/Config/` 下三个 JSON 文件都在。不在的话报错，告诉用户先 `git clone https://github.com/Raphire/Win11Debloat.git`。

### 步骤 2：复制一份英文版

```bash
cp -r Win11Debloat/ Win11Debloat-cn/
```

> 输出目录名默认 `Win11Debloat-cn`，如果用户给了别的名字就用用户的。永远不改英文原版。

### 步骤 3：读 SKILL.md，翻译三个文件

打开 `Win11Debloat-skill-zh/SKILL.md`，仔细读完。然后对照翻译：

| 文件 | 改什么 | 别碰 |
|---|---|---|
| `Config/Features.json` | Label、ToolTip、ApplyText、UndoLabel、ApplyUndoText、UiGroup 的 Label/ToolTip/Values | FeatureId、Category.Name、RegistryKey、GroupId |
| `Config/Apps.json` | Description | FriendlyName、AppId、Recommendation |
| `Config/DefaultSettings.json` | 什么都不改 | 全部不动 |

### 步骤 4：写回文件（带 BOM）

三个 JSON 文件必须以 `encoding='utf-8-sig'` 写回。

> 为什么？PowerShell 遇到不带 BOM 的 UTF-8 文件会按 GBK 解码，所有中文变乱码。忘了这步等于白干。

### 步骤 5：自检

翻完之后跑这几项，确保没问题再告诉用户：

- [ ] Label 全部中文化，没有漏掉的英文
- [ ] ApplyText 全部中文化，`null` 的空位不算漏（EN 原版就没有）
- [ ] UndoLabel 全部中文化 —— **这个最容易漏，旧方案就栽在这里**
- [ ] ApplyUndoText 全部中文化
- [ ] ToolTip 全部中文化
- [ ] Apps.json 的 Description 全部中文化
- [ ] Category.Name 没有被翻成中文（翻了就完蛋，所有 Feature 归属断裂）
- [ ] 三个文件都有 BOM

## 高频错误（禁止事项）

| ❌ 你做错了 | ✅ 应该这样 |
|---|---|
| 把 Category.Name 翻成中文 | 原封不动保留英文 |
| 翻译 FeatureId、AppId、FriendlyName | 这些是标识符，不翻 |
| 省略 UndoLabel 或 ApplyUndoText | 每条都要翻，即便 EN 原版里就有 null |
| 写文件不用 `utf-8-sig` | 三个文件全部用 `utf-8-sig` |
| 用英文引号 `""` | 用 CJK 引号 `「」` |
| 把 DisableUpdateASAP 翻成"阻止" | 注册表操作是 Turn Off，必须用"关闭" |
| 中英文挤在一起 | `禁用Windows` → `禁用 Windows` |
| 翻译时参考旧版 Win11Debloat-cn | 永远只看英文原版，旧版可能有错 |

## 翻译完了怎么告诉用户

简洁输出：

```
翻译完成。Win11Debloat-cn/ 统计：
  Features.json：100 Label、68 ToolTip、99 ApplyText、79 UndoLabel、79 ApplyUndoText → 全部中文
  Apps.json：147 Description → 全部中文
  三个文件均已写入 UTF-8 BOM
```

然后问一句："要我跑质量检查吗？"

接着告诉用户部署方式：

> 翻译后的 `Win11Debloat-cn/` 是完整复制的项目，直接 `.\Win11Debloat-cn\Win11Debloat.ps1` 即可运行。也可以把三个 JSON 覆盖回英文原版的 Config 目录用原版运行。

## 你还要知道

- SKILL.md 是唯一的翻译规范来源。如果 SKILL.md 和 AGENTS.md 有矛盾，以 SKILL.md 为准。
- 英文原版 Win11Debloat 的结构是会变的。翻之前看一眼 Features 数量和 Apps 数量，翻完之后数量必须和原版一致。
- 如果你不清楚某个字段该不该翻，原则是：**标识符不翻，用户可见的文本翻**。
