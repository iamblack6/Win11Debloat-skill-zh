---
name: Win11Debloat-skill-zh
description: 将 Win11Debloat 英文原版 Config JSON 文件完整汉化，以英文为唯一骨架逐字段翻译
---

# Win11Debloat 中文本地化翻译规范

> **路径约定**：本 Skill 假设工作目录下存在英文原版 `Win11Debloat/`，输出到 `Win11Debloat-cn/`（或用户指定的目录名）。如果当前工作目录结构不同，先向用户确认源目录位置。

## 流程总览

```
  英文原版 Win11Debloat/
       │
       ├─ cp -r → Win11Debloat-cn/
       │
       └─ 逐文件翻译 Config/
            │
     ┌──────▼──────┐
     │ 1. 复制项目  │  cp -r 英文原版 → 输出目录（不改原版）
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │ 2. Labels   │  100 个 feature Label + 9 UiGroups 标签 → 中文
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │ 3. ToolTips │  68 条长篇描述 → 中文
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │ 4. ApplyText│  99 条执行状态文本 → "正在..." 句式
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │ 5. Undo★    │  79 UndoLabel + 79 ApplyUndoText → 中文
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │ 6. Apps     │  147 个应用 Description → 中文
     └──────┬──────┘
            │
      ┌──────▼──────┐
      │ 7. BOM 写入  │  三个文件 utf-8-sig，否则 PowerShell 炸
      └──────┬──────┘
             │
      ┌──────▼──────┐
      │ 8. 质量校验  │  残留英文 / null 字段 / 语义 / BOM
      └──────┬──────┘
             │
      ┌──────▼──────┐
      │ 9. 对照验证  │  读取官方 Wiki，逐条对照英文原文检查翻译是否准确
      └─────────────┘
```

> **核心原则**：以英文原版为**唯一骨架**，不做旧版合并、不做 Action 拼接。每个字段独立翻译，不留英文残余。

## 输入

- **英文原版** `Win11Debloat/`（唯一定义结构的来源）
- **输出目录** 如 `Win11Debloat-cn/`（`cp -r` 复制出来，只改 Config 下三个 JSON）

## 翻译约定

| 规则 | 说明 | 示例 |
|---|---|---|
| 品牌名不译 | Windows / Edge / Copilot / OneDrive / Xbox / BitLocker / Brave / HP / Lenovo / Dell / Bing / Skype / LinkedIn / TikTok / Spotify / Netflix 等 | `Disable Microsoft Copilot` → `禁用 Microsoft Copilot` |
| UI 引号 | 统一用 `「」`（不用 `""`） | `"All Apps"` → `「所有应用」` |
| 中文与拉丁字符间距 | CJK **字符**（非标点）与 `[A-Za-z0-9]` 间加空格。但 **CJK 全角标点与拉丁字符间无需额外空格**：`Chat（立即开会）` 不写 `Chat （`、`Edge。` 不写 `Edge 。`、`（AI）` 不写 `（ AI ）` | `禁用Windows` → `禁用 Windows` |
| 符号间距 | 半角符号（如 `/`）前后涉及 CJK 字符时加空格 | `游戏/屏幕` → `游戏 / 屏幕` |
| 动词对照 | Disable→禁用, Enable→启用, Hide→隐藏, Show→显示, Prevent→阻止, Allow→允许, Remove→卸载/移除, Block→阻止, Turn Off→关闭 | |
| ApplyText 句式 | 统一用 `正在...` | `Removing...` → `正在卸载...` |
| ApplyUndoText 句式 | 统一用 `正在...`（撤销时执行的文本） | `Enabling...` → `正在启用...` |
| ToolTip 句式 | 统一用 `此设置将...` 或 `此设置会...` | `This will disable...` → `此设置将禁用...` |

## 各字段翻译要点

### Feature Label（100 条）

直接翻译英文 Label。注意：`Categories[].Name` **不翻译**（是标识符）。

区分两种模式：

| 英文 Pattern | 中文 Pattern | 示例 |
|---|---|---|
| `Disable/Enable/Hide/Show + 名词短语` | 动词 + 名词短语 | `Disable telemetry` → `禁用遥测` |
| 纯描述性（无动词） | 直译描述 | `Drive letter position` → `驱动器号显示位置` |

**特殊情况**：
- `DisableUpdateASAP` — 注册表操作是 Turn Off，Label 用 `关闭尽快获取更新功能` 不用 `阻止`（尽管 EN Label 用了 "Prevent"）。ApplyText 同理：`正在关闭 Windows 尽快获取更新功能`
- `DisableMouseAcceleration` — 英文含义是"鼠标加速"，Windows 内用"提高指针精确度"，应写作 `禁用鼠标加速（提高指针精确度）`
- `PreventUpdateAutoReboot` — 用 `阻止登录后更新自动重启`（此条 EN Label 动词确为 Prevent，无歧义）

### UiGroup Label / Value（9 组）

UiGroup 的 `Label`、`ToolTip`、`Values[].Label` 均需翻译。

**UiGroup Label 翻译要点**：
- 补全介词使中文通顺：`Combine taskbar buttons on the main display` → `在主显示器上合并任务栏按钮`（不是 `主显示器上合并`）
- 包含 EN 中的所有场景信息：`Show tabs from apps when snapping or pressing Alt+Tab` → `贴靠或按 Alt+Tab 时显示应用中的标签页`（不是省略 `贴靠或`）
- 用字准确：`Remove pinned apps` → `移除` 而非 `清除`

**UiGroup Value Label 翻译要点**：
- 保持简洁，不加多余后缀：EN 为 `Grid` → `网格`（不是 `网格视图`）
- 品牌名/路径名不译但引号用 `「」`

### ApplyText（99 条）

执行时状态文本，对应注册表操作注释。**必须全部翻译**：

- `Disabling...` → `正在禁用...`
- `Enabling...` → `正在启用...`
- `Hiding...` → `正在隐藏...`
- `Showing...` → `正在显示...`
- `Removing...` → `正在卸载...` / `正在清除...`
- `Setting...` → `正在设置...`
- `Changing...` → `正在更改...`
- `Preventing...` → `正在阻止...` / `正在关闭...`（**视注册表操作而定**：如 `DisableUpdateASAP` 注册表操作是 Turn Off，ApplyText 用 `正在关闭...`；`PreventUpdateAutoReboot` 则是真正的阻止行为，用 `正在阻止...`）
- `Turning off...` → `正在关闭...`
- `Adding...` → `正在添加...`

### UndoLabel + ApplyUndoText（各 79 条）

**最容易遗漏**，旧方案因合并逻辑无法处理这两个字段，导致全英。直接从英文翻译：

- `Enable telemetry` → `启用遥测、跟踪和定向广告`
- `Show 'Home' from navigation pane` → `显示导航窗格中的「主页」`
- `使用默认任务栏合并行为` 等

ApplyUndoText 同样全部 `正在...` 句式。

### ToolTip（68 条）

长篇解释文本。翻译要点：
- 开头统一 `此设置将...`（不用 `这将...` / `此功能将...`）
- 注册表注释如 "This feature uses policies, which will lock down certain settings" → `此功能使用策略，部分设置将被锁定。`
- WARNING 保留重要程度但语气自然化
- 保持英文原文的信息密度，不增不减

### Apps.json（147 条）

仅翻译 `Description` 字段。`FriendlyName` / `AppId` 不译。`Recommendation` 不译。

| 类型 | 示例 |
|---|---|
| Microsoft 应用 | `Video editor from Microsoft` → `Microsoft 出品的视频编辑器` |
| 第三方应用 | `Spotify music streaming app` → `Spotify 音乐流媒体应用` |
| OEM 软件 | `HP OEM software for support` → `HP OEM 支持、更新和故障排除软件` |
| 系统组件 | `Runtime required for Windows Widgets` → `Windows Widgets 运行所需的运行时` |
| 重要警告保留 | `WARNING: This app cannot be reinstalled easily if removed!` → `警告：此应用移除后难以重新安装！` |

### DefaultSettings.json

仅 Features.json 的 FeatureId 引用列表。**无需翻译**，仅需确保条目数与英文原版一致。

## UTF-8 BOM

三个 JSON 文件写回时**必须**带 `EF BB BF`（Python: `encoding='utf-8-sig'`）。

> Windows PowerShell `Get-Content -Raw` 读取无 BOM UTF-8 文件时按系统默认 ANSI（中文 GBK）解码，导致中文损坏、`ConvertFrom-Json` 解析失败。

## 关键陷阱

### Category `Name` 是标识符，不许翻译

`Features.json` 中 `Categories[].Name` 是 Feature 的 `Category` 字段引用的标识符，**必须保持英文原文**。翻译后会导致 84+ 个 feature 归属断裂。

```
EN:  Category.Name = "Privacy & Suggested Content"
     Feature.Category = "Privacy & Suggested Content"  ← 匹配 ✓

WRONG:  Category.Name = "隐私与推荐内容"
        Feature.Category = "Privacy & Suggested Content"  ← 不匹配 ✗
```

其他 **不许翻译** 的标识符字段：
- `FeatureId`
- `DefaultSettings.json` 中的 `Name`（引用 FeatureId）
- `Apps.json` 中的 `AppId`、`FriendlyName`
- UiGroup 中的 `GroupId`

## 质量校验清单

全部通过才算完成：

- [ ] 所有 Label 中文化（`all(ord(c) < 128 for c in label)` 检查 Pass）
- [ ] 所有 ApplyText 中文化，无遗漏 null
- [ ] 所有 UndoLabel 中文化
- [ ] 所有 ApplyUndoText 中文化
- [ ] 所有 ToolTip 中文化
- [ ] Apps.json 147 个 Description 全部中文
- [ ] Labels 无语义反向（disable 译成了 enable、Turn Off 译成了 Prevent 等）
- [ ] **CJK-Latin 间距正确**：CJK 字符（非标点）与拉丁字母间有空格（`禁用Windows` → `禁用 Windows`）；CJK 全角标点与拉丁间无需空格（`Chat（` 不写 `Chat （`）；半角符号 `/` 前后有 CJK 时有空格
- [ ] **Feature.Category 全部与 Category.Name 匹配**（Category.Name 不翻译则自动满足）
- [ ] UiGroup Values 顺序与 EN 一致
- [ ] 三个文件均带 UTF-8 BOM

## 对照官方文档验证

翻译完成后，必须对照官方 Wiki 逐条检查英文原文与中文翻译是否一致：

```
https://github.com/Raphire/Win11Debloat/wiki/Features
```

**检查要点**：
- 每个 feature 的 EN Label 动词是否与中文翻译对应（`Hide` → `隐藏` 而非 `禁用`）
- 语义是否有反向（如"获取更新"实际应为"阻止/关闭获取更新"）
- 品牌名是否正确保留英文
- 长描述（ToolTip）是否遗漏关键信息或擅自增减内容

如果当前环境可访问 GitHub，用 web fetch 读取 Wiki 页面后逐条对照。如果不可访问，跳过此步并告知用户。
