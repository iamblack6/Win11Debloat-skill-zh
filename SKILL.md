---
name: Win11Debloat-i18n
description: Win11Debloat JSON 配置中文本地化管线，支持规则翻译和 LLM 辅助
---

# Win11Debloat 中文本地化管线

一键将 Win11Debloat 英文配置界面翻译为简体中文。

## 快速开始

```bash
# 1. 克隆本项目和英文原版
git clone https://github.com/iamblack6/Win11Debloat-skill-zh.git
cd Win11Debloat-skill-zh
git clone https://github.com/Raphire/Win11Debloat.git

# 2. 安装依赖
pip install pyyaml

# 3. 一键翻译
python cli.py zh-CN
```

输出 `Win11Debloat-zh/`，直接运行：

```powershell
.\Win11Debloat-zh\Win11Debloat.ps1
```

## 翻译管线

```
Extract → Translate → Assemble → Validate
```

| 步骤 | 文件 | 说明 |
|---|---|---|
| Extract | `pipeline/extract.py` | 从英文 JSON 拆出 621 个独立翻译单元 |
| Translate | `pipeline/translate.py` | 规则优先（glossary + patterns + overrides），可接参考译文回填 |
| Assemble | `pipeline/assemble.py` | 重组 JSON 结构，自动写入 UTF-8 BOM |
| Validate | `pipeline/validate.py` | 校验标识符完整、字段数一致、无漏翻 |

## 翻译策略

翻译引擎按优先级执行：

1. **Override** — 硬编码特例（`languages/zh-CN/overrides.yaml`）
2. **Glossary 精确匹配** — 术语表整句命中（`languages/zh-CN/glossary.yaml`）
3. **句式模板** — 正则替换（`languages/zh-CN/patterns.yaml`）
4. **词汇级替换** — 术语表子串替换
5. **参考回填** — 从已有中文译本填充（`-r Win11Debloat-cn/`）

未命中项可通过 LLM API 翻译（接口已预留，见 `pipeline/translate.py:llm_translate()`）。

## 添加新语言

```bash
mkdir -p languages/ja
cp languages/zh-CN/*.yaml languages/ja/
# 编辑 glossary.yaml → 替换为日语术语
# 编辑 patterns.yaml → 替换为日语句式
# 编辑 overrides.yaml → 替换为日语特例
python cli.py ja
```

## 目录结构

```
Win11Debloat-skill-zh/
├── cli.py                    # 总入口
├── pipeline/
│   ├── extract.py            # 提取翻译单元
│   ├── translate.py          # 翻译引擎
│   ├── assemble.py           # 重组 JSON + BOM
│   └── validate.py           # 质量校验
├── languages/zh-CN/
│   ├── glossary.yaml         # 术语表
│   ├── patterns.yaml         # 句式模板
│   └── overrides.yaml        # 特例覆盖
└── SKILL.md                  # 你正在读的文件
```

## 许可

MIT
