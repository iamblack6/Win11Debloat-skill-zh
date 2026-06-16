
import json, re, sys
from pathlib import Path
import yaml

def load_config(lang_dir):
    config = {}
    for name in ["glossary", "patterns", "overrides"]:
        p = Path(lang_dir) / f"{name}.yaml"
        if p.exists():
            with open(p, encoding="utf-8") as f:
                config[name] = yaml.safe_load(f) or {}
    return config

def build_overrides(overrides):
    lookup = {}
    for ov in overrides.get("overrides", []):
        kt = ov["key"]
        if kt in ("UiGroup.Label", "UiGroup.ToolTip"):
            key = (kt, str(ov["group_id"]))
        elif kt == "UiGroup.Value":
            key = (kt, str(ov["group_id"]), str(ov["value"]))
        elif kt.startswith("Feature.") or kt == "App.Description":
            fid = ov.get("feature_id") or ov.get("app_id") or ov.get("friendly_name", "")
            key = (kt, str(fid))
        else:
            continue
        lookup[key] = ov["translation"]
    return lookup

def build_ref_lookup(ref_dir, source_dir=None):
    """Build reference lookup. For UiGroup.Value, match by (group_id, en_text) -> zh_text."""
    ref = Path(ref_dir)
    fp = ref / "Config" / "Features.json"
    ap = ref / "Config" / "Apps.json"
    if not fp.exists():
        return {}
    cf = json.load(open(fp, encoding="utf-8-sig"))
    ca = json.load(open(ap, encoding="utf-8-sig")) if ap.exists() else {}

    # Load EN source for UiGroup.Value matching
    en_groups = {}
    if source_dir:
        en_fp = Path(source_dir) / "Config" / "Features.json"
        if en_fp.exists():
            en_f = json.load(open(en_fp, encoding="utf-8"))
            for g in en_f.get("UiGroups", []):
                en_groups[g["GroupId"]] = [v.get("Label", "") for v in g.get("Values", [])]

    lookup = {}
    cn_feats = {f["FeatureId"]: f for f in cf.get("Features", [])}
    cn_groups = {g["GroupId"]: g for g in cf.get("UiGroups", [])}

    for fid, feat in cn_feats.items():
        for field in ["Label", "ToolTip", "ApplyText", "UndoLabel", "ApplyUndoText"]:
            zh = feat.get(field, "")
            if zh:
                lookup[("Feature." + field, fid)] = zh

    for gid, group in cn_groups.items():
        zh = group.get("Label", "")
        if zh:
            lookup[("UiGroup.Label", gid)] = zh
        zh = group.get("ToolTip", "")
        if zh:
            lookup[("UiGroup.ToolTip", gid)] = zh
        cn_vals = group.get("Values", [])
        en_vals = en_groups.get(gid, [])
        for i, v in enumerate(cn_vals):
            zh = v.get("Label", "")
            if zh:
                if i < len(en_vals):
                    # Match by EN text
                    lookup[("UiGroup.Value", gid, en_vals[i])] = zh
                else:
                    # Fallback: match by position
                    lookup[("UiGroup.Value", gid, i)] = zh

    for a in ca.get("Apps", []):
        aid = a["AppId"]
        if isinstance(aid, list):
            aid = aid[0]
        zh = a.get("Description", "")
        if zh:
            lookup[("App.Description", aid)] = zh

    return lookup

def translate(units, config, ref_lookup=None):
    """Priority: override > reference > glossary_exact > pattern > glossary_fallback"""
    glossary = config.get("glossary", {})
    ov_lookup = build_overrides(config.get("overrides", {}))
    patterns = config.get("patterns", {})
    hit = 0

    for u in units:
        en = u["en"].strip()
        if not en:
            continue
        t = u["type"]

        # Build lookup key
        key = None
        if t.startswith("Feature."):
            key = (t, str(u.get("feature_id", "")))
        elif t == "UiGroup.Label":
            key = (t, str(u.get("group_id", "")))
        elif t == "UiGroup.ToolTip":
            key = (t, str(u.get("group_id", "")))
        elif t == "UiGroup.Value":
            key = (t, str(u.get("group_id", "")), en)
        elif t == "App.Description":
            key = (t, str(u.get("app_id", "")))

        # 1. Override
        if key and key in ov_lookup:
            u["zh"] = ov_lookup[key]
            u["method"] = "override"
            hit += 1
            continue

        # 2. Reference backfill
        if key and ref_lookup and key in ref_lookup:
            u["zh"] = ref_lookup[key]
            u["method"] = "reference"
            hit += 1
            continue

        # 3. Glossary exact
        if en in glossary:
            u["zh"] = glossary[en]
            u["method"] = "glossary_exact"
            hit += 1
            continue

        # 4. Pattern match
        matched = False
        if t == "Feature.ApplyText":
            for tm in patterns.get("apply_text", []):
                m = re.match(tm["pattern"], en)
                if m:
                    u["zh"] = re.sub(tm["pattern"], tm["replacement"], en)
                    u["method"] = "pattern"
                    matched = True; hit += 1
                    break
        if not matched and t in ("Feature.Label", "Feature.UndoLabel"):
            for tm in patterns.get("labels", []):
                m = re.match(tm["pattern"], en)
                if m:
                    u["zh"] = re.sub(tm["pattern"], tm["replacement"], en)
                    u["method"] = "pattern"
                    matched = True; hit += 1
                    break
        if not matched and t == "Feature.ToolTip":
            for tm in patterns.get("tooltips", []):
                m = re.match(tm["pattern"], en)
                if m:
                    u["zh"] = re.sub(tm["pattern"], tm["replacement"], en)
                    u["method"] = "pattern"
                    matched = True; hit += 1
                    break
        if matched:
            continue

        # 5. Glossary fallback
        zh = en
        changed = False
        for term in sorted(glossary.keys(), key=len, reverse=True):
            if term in zh and term != zh and len(term) > 2:
                zh = zh.replace(term, glossary[term])
                changed = True
        if changed and zh != en:
            u["zh"] = zh
            u["method"] = "glossary_fallback"
            hit += 1
            continue

        u["zh"] = ""
        u["method"] = "unmatched"

    miss = sum(1 for u in units if not u["zh"])
    return units, hit, miss

def run(units_file, lang_dir, output_file, ref_dir=None):
    units = json.load(open(units_file, encoding="utf-8"))
    config = load_config(lang_dir)

    # Detect source dir (parent of output_file's grandparent? use ref_dir's sibling)
    source_dir = None
    if ref_dir:
        source_dir = Path(ref_dir).parent / "Win11Debloat"
        if not (source_dir / "Config" / "Features.json").exists():
            source_dir = None

    ref_lookup = build_ref_lookup(ref_dir, source_dir) if ref_dir else {}
    units, hit, miss = translate(units, config, ref_lookup)
    print(f"translated: {hit}/{len(units)}, unmatched: {miss}")

    if miss > 0:
        um = [u for u in units if not u["zh"]]
        print(f"WARNING: {miss} unmatched:")
        for u in um[:10]:
            print(f"  [{u['type']}] {u['en'][:70]}")

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    json.dump(units, open(output_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    methods = {}
    for u in units:
        m = u.get("method", "unknown")
        methods[m] = methods.get(m, 0) + 1
    print(f"methods: {dict(sorted(methods.items()))}")
    return units

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("units", type=Path)
    p.add_argument("lang", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("-r", "--reference", type=Path)
    a = p.parse_args()
    run(a.units, a.lang, a.output, a.reference)
