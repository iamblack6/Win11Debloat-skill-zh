# Win11Debloat-skill-zh

把 Win11Debloat 的英文配置界面翻译成中文——这是一份 AI Skill，翻译好的成品可参考右侧 Release。

## 这是什么

[Win11Debloat](https://github.com/Raphire/Win11Debloat) 是一个 Windows 11 优化工具，能一键关掉广告、遥测、预装应用。但它的 400+ 个配置项全是英文的。

`Win11Debloat-skill-zh` 是一份"AI 翻译说明书"（Skill）。你把它喂给任意 AI（Cursor、ChatGPT、Claude、Cline……都可以），AI 就能照着规则把英文配置逐条翻译成中文，而且不会乱码、不会翻坏标识符、不会漏字段。

> **已测试版本**：[Win11Debloat v2026.06.11](https://github.com/Raphire/Win11Debloat/releases/tag/2026.06.11) 工作正常。

## 快速开始

```bash
git clone https://github.com/iamblack6/Win11Debloat-skill-zh.git
cd Win11Debloat-skill-zh
```

在当前目录启动你的 AI 工具（Claude、opencode、Codex 等），在对话框中输入：

> **运行这个项目**

AI 会自动完成翻译，生成 `Win11Debloat-cn/`。最后在 Windows 上执行：

```powershell
.\Win11Debloat-cn\Win11Debloat.ps1
```

## 5 分钟搞定

### 第 1 步：创建工作目录

```bash
mkdir my-debloat-cn
cd my-debloat-cn
```

### 第 2 步：下载翻译规则（本项目）

```bash
git clone https://github.com/iamblack6/Win11Debloat-skill-zh.git
```

### 第 3 步：下载英文原版

```bash
git clone https://github.com/Raphire/Win11Debloat.git
```

完成后目录长这样：

```
my-debloat-cn/
├── Win11Debloat-skill-zh/    # 翻译规则（SKILL.md 在里头）
│   ├── SKILL.md        # ← AI 就读这个
│   ├── AGENTS.md
│   └── README.md
└── Win11Debloat/       # 英文原版
    └── Config/
        ├── Features.json
        ├── Apps.json
        └── DefaultSettings.json
```

### 第 4 步：把 SKILL.md 喂给 AI

打开你用的 AI 工具，把 `Win11Debloat-skill-zh/SKILL.md` 丢进去，然后说：

> 按照 SKILL.md 的翻译规范，把 `Win11Debloat/` 翻译成中文，输出到 `Win11Debloat-cn/`。

就这么一句话。AI 会自动完成全部翻译。

**各种工具怎么投喂：**

| 工具 | 操作 |
|---|---|
| Cursor | 把 `SKILL.md` 拖进侧边栏，然后在 Composer 里发指令 |
| Cline | 对话里 `@SKILL.md`，再输入指令 |
| ChatGPT / Claude 网页版 | 复制 SKILL.md 全文，粘贴进对话框，附上指令 |
| Gemini | 上传 SKILL.md 作为附件，输入指令 |
| Continue | 用 `@file` 引用 SKILL.md |
| Windsurf | 放进 `.windsurfrules`，或者直接 @ 引用 |
| Copilot | 放进 `.github/copilot-instructions.md` |

### 第 5 步：检查结果

AI 跑完后，生成的文件在 `Win11Debloat-cn/`（或你指定的目录名）。可以跑这几行验证：

```bash
# 检查 BOM（没有 BOM 的话 PowerShell 会乱码）
python3 -c "
for f in ['Features.json','Apps.json','DefaultSettings.json']:
    with open(f'Win11Debloat-cn/Config/{f}','rb') as fp:
        ok = fp.read(3).hex() == 'efbbbf'
    print(f'{f}: {\"OK\" if ok else \"MISSING BOM\"}')"

# 检查有没有漏翻的英文
python3 -c "
import json
d = json.load(open('Win11Debloat-cn/Config/Features.json', encoding='utf-8-sig'))
en = [f['FeatureId'] for f in d['Features']
      if f.get('UndoLabel') and all(ord(c)<128 for c in f['UndoLabel'].replace(\"'\",'').replace('-','').replace(' ',''))]
print(f'UndoLabel 英文残留: {len(en)} 条') if en else print('全部中文，OK')"
```

全部 OK 就说明翻译成功。把 `Win11Debloat-cn/` 里的文件替换到 Win11Debloat 原项目里就能用了。

## 翻什么、不翻什么

| 文件 | 翻的内容 | 不动的（标识符，动了就坏） |
|---|---|---|
| Features.json | Label、ToolTip、ApplyText、UndoLabel、ApplyUndoText | FeatureId、Category.Name、RegistryKey |
| Apps.json | Description | FriendlyName、AppId、Recommendation |
| DefaultSettings.json | 全都不翻 | 都是 ID 引用 |

## 规则速览

| 规则 | 例子 |
|---|---|
| 品牌名不译 | `Disable Microsoft Copilot` → `禁用 Microsoft Copilot` |
| 引号用 `「」` | `"All Apps"` → `「所有应用」` |
| 中英文间加空格 | `禁用Windows` → `禁用 Windows` |
| `DisableUpdateASAP` 用「关闭」 | 注册表操作是 Turn Off，不用「阻止」 |
| Category.Name 不要碰 | 动了会导致所有功能列表错乱 |
| 文件必须 UTF-8 BOM | 否则 PowerShell 打开变乱码 |

## 原理

翻译前 AI 看到的是：

```json
{ "FeatureId": "DisableTelemetry", "Label": "Disable telemetry, tracking & targeted ads" }
```

翻译后：

```json
{ "FeatureId": "DisableTelemetry", "Label": "禁用遥测、跟踪和定向广告" }
```

FeatureId 没碰，Label 翻了——这就是整份 SKILL.md 的核心逻辑：**标识符不动，用户看的文本翻译**。

## 常见问题

**Q: 为什么不用现成的翻译软件？**

因为翻译软件不认识 Category.Name 是标识符，翻了就坏。而且不会自动加 BOM，PowerShell 读不了。

**Q: 翻译完怎么用？**

两种方式：

- **替换原版**：把 `Win11Debloat-cn/Config/` 下的三个 JSON 覆盖到英文原版 `Win11Debloat/Config/`，然后运行 `Win11Debloat\Win11Debloat.ps1`
- **直接运行**：本 Skill 通过完整复制项目目录来创建翻译副本，`Win11Debloat-cn/` 本身就是可运行项目，直接 `.\Win11Debloat-cn\Win11Debloat.ps1` 即可

**Q: 项目更新了怎么办？**

重新 clone 最新英文原版，再喂一次 SKILL.md 给 AI。翻译规则是稳定的，英文变多少都能处理。

## 许可

MIT
