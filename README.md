# Win11Debloat-skill-zh

一键将 [Win11Debloat](https://github.com/Raphire/Win11Debloat) 的英文配置界面翻译为简体中文。

Win11Debloat 是 Windows 11 优化工具，能关闭广告、遥测、预装应用——但 400+ 配置项全是英文。本项目提供一条命令完成全部翻译，自动处理 UTF-8 BOM、标识符保护和 CJK 排版。

> 已测试 [Win11Debloat v2026.06.11](https://github.com/Raphire/Win11Debloat/releases/tag/2026.06.11)

## 快速开始

```bash
git clone https://github.com/iamblack6/Win11Debloat-skill-zh.git
cd Win11Debloat-skill-zh
git clone https://github.com/Raphire/Win11Debloat.git
pip install pyyaml
python cli.py zh-CN
```

输出 `Win11Debloat-zh/`，在 Windows 上运行：

```powershell
.\Win11Debloat-zh\Win11Debloat.ps1
```

## 翻译管线

```
Extract → Translate → Assemble → Validate
```

| 步骤 | 做什么 | 结果 |
|---|---|---|
| Extract | 从英文 JSON 拆出 621 个独立翻译单元 | 扁平 JSON |
| Translate | 规则优先翻译 + 参考译文回填 | 100% 覆盖 |
| Assemble | 重组 JSON 结构 + 写 UTF-8 BOM | 完整项目 |
| Validate | BOM / 标识符 / 字段数 / 漏翻检查 | PASS / FAIL |

## 翻译策略

引擎按优先级逐级命中，未命中时才回退到参考译文或 LLM：

1. **Override** — 硬编码特例（如 `DisableUpdateASAP` → 关闭）
2. **Glossary 精确匹配** — 术语表整句命中
3. **句式模板** — 正则替换（`Disable X` → 禁用 X）
4. **词汇级替换** — 术语表子串替换
5. **参考回填** — 从已有中文译本填充
6. **LLM 翻译** — 接口已预留，接入 OpenAI/Claude/DeepSeek 即可

所有翻译规则集中在 `languages/zh-CN/` 下三个 YAML 文件：

```yaml
# glossary.yaml — 术语表
Disable: 禁用
Microsoft: Microsoft    # 品牌名不译
"File Explorer": 文件资源管理器

# patterns.yaml — 句式模板
- pattern: '^Disable (.+)$'
  replacement: '禁用 \1'

# overrides.yaml — 特例
- key: Feature.Label
  feature_id: DisableUpdateASAP
  translation: 关闭尽快获取更新功能
```

## 翻什么、不翻什么

| 文件 | 翻译 | 不碰（标识符） |
|---|---|---|
| Features.json | Label、ToolTip、ApplyText、UndoLabel、ApplyUndoText、UiGroup 文本 | FeatureId、Category.Name、RegistryKey、GroupId |
| Apps.json | Description | FriendlyName、AppId、Recommendation |
| DefaultSettings.json | 全部不翻 | FeatureId 引用列表 |

## 添加新语言

```bash
cp -r languages/zh-CN languages/ja
# 编辑 languages/ja/glossary.yaml → 日语术语
# 编辑 languages/ja/patterns.yaml → 日语句式
python cli.py ja
```

## 目录结构

```
Win11Debloat-skill-zh/
├── cli.py                        # 总入口
├── pipeline/
│   ├── extract.py                # 提取翻译单元
│   ├── translate.py              # 翻译引擎
│   ├── assemble.py               # 重组 JSON + BOM
│   └── validate.py               # 质量校验
├── languages/zh-CN/
│   ├── glossary.yaml             # 术语表（100+ 条）
│   ├── patterns.yaml             # 句式模板
│   └── overrides.yaml            # 特例覆盖
├── SKILL.md                      # AI Skill 指引
└── README.md                     # 你正在读的文件
```

## FAQ

**Q: 上游 Win11Debloat 更新了怎么办？**

```bash
cd Win11Debloat && git pull && cd ..
python cli.py zh-CN
```

规则配置与英文版本解耦，新增字段自动提取、翻译、校验。

**Q: 翻译完怎么用？**

两种方式：
- 直接运行 `.\Win11Debloat-zh\Win11Debloat.ps1`
- 把 `Win11Debloat-zh/Config/` 下三个 JSON 覆盖回英文原版

**Q: 为什么不用翻译软件批量翻译？**

翻译软件不认识 Category.Name 是标识符，翻了会导致所有功能归属断裂。本管线的 validate 步骤会严格校验标识符未被篡改。

**Q: 为什么必须 UTF-8 BOM？**

Windows PowerShell `Get-Content` 遇到无 BOM UTF-8 文件会按系统 ANSI（中文 GBK）解码，所有中文变乱码。assemble 步骤自动写入 BOM。

## 许可

MIT
