"""
从英文原版 JSON 中提取所有待翻译字段，输出扁平的翻译单元列表。
每个单元包含：翻译上下文、英文原文、字段类型，供后续 translate 步骤使用。
"""

import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict:
    """加载 JSON，自动处理 BOM。"""
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def extract_features(features: list[dict]) -> list[dict]:
    """从 Features 数组中提取所有可翻译字段。"""
    units = []

    for feat in features:
        fid = feat.get("FeatureId", "?")
        cat = feat.get("Category", "")

        # Label — 始终翻译
        if feat.get("Label"):
            units.append({
                "type": "Feature.Label",
                "feature_id": fid,
                "category": cat or "",
                "en": feat["Label"],
                "zh": "",
            })

        # ToolTip — 部分 feature 有
        if feat.get("ToolTip"):
            units.append({
                "type": "Feature.ToolTip",
                "feature_id": fid,
                "category": cat or "",
                "en": feat["ToolTip"],
                "zh": "",
            })

        # ApplyText — 几乎全部有
        if feat.get("ApplyText"):
            units.append({
                "type": "Feature.ApplyText",
                "feature_id": fid,
                "category": cat or "",
                "en": feat["ApplyText"],
                "zh": "",
            })

        # UndoLabel
        if feat.get("UndoLabel"):
            units.append({
                "type": "Feature.UndoLabel",
                "feature_id": fid,
                "category": cat or "",
                "en": feat["UndoLabel"],
                "zh": "",
            })

        # ApplyUndoText
        if feat.get("ApplyUndoText"):
            units.append({
                "type": "Feature.ApplyUndoText",
                "feature_id": fid,
                "category": cat or "",
                "en": feat["ApplyUndoText"],
                "zh": "",
            })

    return units


def extract_uigroups(uigroups: list[dict]) -> list[dict]:
    """从 UiGroups 中提取 Label、ToolTip、Values[].Label。"""
    units = []

    for group in uigroups:
        gid = group.get("GroupId", "?")

        # Group Label
        if group.get("Label"):
            units.append({
                "type": "UiGroup.Label",
                "group_id": gid,
                "en": group["Label"],
                "zh": "",
            })

        # Group ToolTip
        if group.get("ToolTip"):
            units.append({
                "type": "UiGroup.ToolTip",
                "group_id": gid,
                "en": group["ToolTip"],
                "zh": "",
            })

        # Values[].Label
        for val in group.get("Values", []):
            if val.get("Label"):
                units.append({
                    "type": "UiGroup.Value",
                    "group_id": gid,
                    "feature_ids": val.get("FeatureIds", []),
                    "en": val["Label"],
                    "zh": "",
                })

    return units


def extract_apps(apps: list[dict]) -> list[dict]:
    """从 Apps 中提取 Description 字段。"""
    units = []

    for app in apps:
        if app.get("Description"):
            aid = app.get("AppId", "?")
            if isinstance(aid, list):
                aid = aid[0]  # Edge has ["Microsoft.Edge", "XPFFTQ037JWMHS"]
            units.append({
                "type": "App.Description",
                "app_id": aid,
                "friendly_name": app.get("FriendlyName", ""),
                "en": app["Description"],
                "zh": "",
            })

    return units


def run(source_dir: Path, output_file: Path | None = None):
    """
    从 source_dir/Config/ 读取三个 JSON，提取翻译单元。

    返回 list[dict]，如果指定 output_file 则同时写入 JSON。
    """
    features_path = source_dir / "Config" / "Features.json"
    apps_path = source_dir / "Config" / "Apps.json"

    if not features_path.exists():
        print(f"错误: {features_path} 不存在", file=sys.stderr)
        sys.exit(1)
    if not apps_path.exists():
        print(f"错误: {apps_path} 不存在", file=sys.stderr)
        sys.exit(1)

    features_data = load_json(features_path)
    apps_data = load_json(apps_path)

    units = []
    units.extend(extract_features(features_data.get("Features", [])))
    units.extend(extract_uigroups(features_data.get("UiGroups", [])))
    units.extend(extract_apps(apps_data.get("Apps", [])))

    # 统计
    type_counts = {}
    for u in units:
        t = u["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"提取完成: {len(units)} 个翻译单元")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(units, f, ensure_ascii=False, indent=2)
        print(f"已写入 {output_file}")

    return units


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="提取 Win11Debloat 翻译单元")
    parser.add_argument("source", type=Path, help="英文原版目录 (含 Config/)")
    parser.add_argument("-o", "--output", type=Path, help="输出 JSON 文件路径")
    args = parser.parse_args()

    run(args.source, args.output)
