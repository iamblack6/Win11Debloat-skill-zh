"""
将翻译结果写回 JSON 结构，生成完整的 Win11Debloat-cn/ 项目。
"""

import json
import shutil
import sys
from pathlib import Path


# BOM header
BOM = b"\xef\xbb\xbf"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json_bom(path: Path, data: dict) -> None:
    """以 UTF-8 BOM + 两空格缩进写入 JSON。"""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    with open(path, "wb") as f:
        f.write(BOM + content.encode("utf-8"))


def build_lookup(units: list[dict]) -> dict:
    """
    将翻译单元列表转换为查找字典，支持精确匹配和前缀匹配。
    返回 {(type, id_key): zh_text}
    """
    lookup = {}

    for u in units:
        zh = u.get("zh", "")
        if not zh:
            continue

        t = u["type"]
        en = u["en"]

        if t in ("Feature.Label", "Feature.ToolTip", "Feature.ApplyText",
                 "Feature.UndoLabel", "Feature.ApplyUndoText"):
            key = (t, u["feature_id"])
        elif t.startswith("UiGroup."):
            if t == "UiGroup.Value":
                # Value 用 en 原文匹配
                key = (t, u["group_id"], en)
            else:
                key = (t, u["group_id"])
        elif t == "App.Description":
            key = (t, u["app_id"])
        else:
            continue

        lookup[key] = zh

    return lookup


def apply_cjk_spacing(text: str) -> str:
    """在 CJK 字符与拉丁字符之间插入空格（已有空格的跳过）。"""
    import re

    # CJK 范围 + 日韩
    cjk = (
        r"\u4e00-\u9fff"      # CJK Unified
        r"\u3400-\u4dbf"      # CJK Extension A
        r"\uf900-\ufaff"      # CJK Compatibility
        r"\u3040-\u309f"      # Hiragana
        r"\u30a0-\u30ff"      # Katakana
        r"\uac00-\ud7af"      # Hangul
    )

    # CJK 字符后接 Latin 字母/数字 → 加空格
    text = re.sub(rf"([{cjk}])([A-Za-z0-9])", r"\1 \2", text)
    # Latin 字母/数字后接 CJK 字符 → 加空格
    text = re.sub(rf"([A-Za-z0-9])([{cjk}])", r"\1 \2", text)

    # 半角 / 前后有 CJK → 加空格
    text = re.sub(rf"([{cjk}])/([{cjk}])", r"\1 / \2", text)
    text = re.sub(rf"([{cjk}])/([A-Za-z0-9])", r"\1 / \2", text)
    text = re.sub(rf"([A-Za-z0-9])/([{cjk}])", r"\1 / \2", text)

    return text


def assemble_features(features_data: dict, lookup: dict) -> dict:
    """将翻译写回 Features.json 结构。"""
    import copy

    result = copy.deepcopy(features_data)

    # Features
    for feat in result.get("Features", []):
        fid = feat.get("FeatureId", "")

        for field, unit_type in [
            ("Label", "Feature.Label"),
            ("ToolTip", "Feature.ToolTip"),
            ("ApplyText", "Feature.ApplyText"),
            ("UndoLabel", "Feature.UndoLabel"),
            ("ApplyUndoText", "Feature.ApplyUndoText"),
        ]:
            key = (unit_type, fid)
            if key in lookup:
                feat[field] = apply_cjk_spacing(lookup[key])

    # UiGroups
    for group in result.get("UiGroups", []):
        gid = group.get("GroupId", "")

        # Group Label
        key = ("UiGroup.Label", gid)
        if key in lookup:
            group["Label"] = apply_cjk_spacing(lookup[key])

        # Group ToolTip
        key = ("UiGroup.ToolTip", gid)
        if key in lookup:
            group["ToolTip"] = apply_cjk_spacing(lookup[key])

        # Values
        for val in group.get("Values", []):
            en_label = val.get("Label", "")
            key = ("UiGroup.Value", gid, en_label)
            if key in lookup:
                val["Label"] = apply_cjk_spacing(lookup[key])

    return result


def assemble_apps(apps_data: dict, lookup: dict) -> dict:
    """将翻译写回 Apps.json 结构。"""
    import copy

    result = copy.deepcopy(apps_data)

    for app in result.get("Apps", []):
        aid = app.get("AppId", "")
        if isinstance(aid, list):
            aid = aid[0]
        key = ("App.Description", aid)
        if key in lookup:
            app["Description"] = apply_cjk_spacing(lookup[key])

    return result


def run(source_dir: Path, units_file: Path, output_dir: Path) -> None:
    """
    source_dir: 英文原版目录
    units_file: 翻译单元 JSON（含 zh 字段）
    output_dir: 输出目录（如 Win11Debloat-cn/）
    """
    # 载入翻译单元
    with open(units_file, "r", encoding="utf-8") as f:
        units = json.load(f)

    lookup = build_lookup(units)
    translated_count = len(lookup)
    total_count = len(units)
    print(f"翻译覆盖率: {translated_count}/{total_count} ({translated_count * 100 // total_count}%)")

    if translated_count == 0:
        print("错误: 没有翻译数据，请先运行翻译步骤", file=sys.stderr)
        sys.exit(1)

    # 复制整个项目
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(source_dir, output_dir, symlinks=False,
                    ignore=shutil.ignore_patterns(".git"))

    # 删除复制过来的 .git 残留
    git_dir = output_dir / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)

    # 翻译 Features.json
    features_path = source_dir / "Config" / "Features.json"
    features_data = load_json(features_path)
    translated_features = assemble_features(features_data, lookup)
    write_json_bom(output_dir / "Config" / "Features.json", translated_features)
    print("Features.json → 已写入 (UTF-8 BOM)")

    # 翻译 Apps.json
    apps_path = source_dir / "Config" / "Apps.json"
    apps_data = load_json(apps_path)
    translated_apps = assemble_apps(apps_data, lookup)
    write_json_bom(output_dir / "Config" / "Apps.json", translated_apps)
    print("Apps.json → 已写入 (UTF-8 BOM)")

    # DefaultSettings.json — 只复制，不翻译，但要 BOM
    defaults_path = source_dir / "Config" / "DefaultSettings.json"
    defaults_data = load_json(defaults_path)
    write_json_bom(output_dir / "Config" / "DefaultSettings.json", defaults_data)
    print("DefaultSettings.json → 已写入 (UTF-8 BOM，未翻译)")

    print(f"\n翻译完成 → {output_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="将翻译结果组装成 Win11Debloat-cn/")
    parser.add_argument("source", type=Path, help="英文原版目录")
    parser.add_argument("units", type=Path, help="翻译单元 JSON 文件")
    parser.add_argument("output", type=Path, help="输出目录")
    args = parser.parse_args()

    run(args.source, args.units, args.output)
