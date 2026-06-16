
"""
Translation quality validation.
Checks: identifiers intact, field counts match, untranslated residuals, BOM.
"""
import json, sys
from pathlib import Path

def has_bom(path):
    with open(path, "rb") as f:
        return f.read(3) == b"\xef\xbb\xbf"

def validate_residual(en_path, cn_path):
    en_data = json.load(open(en_path, "r", encoding="utf-8-sig"))
    cn_data = json.load(open(cn_path, "r", encoding="utf-8-sig"))
    en_feats = {f["FeatureId"]: f for f in en_data.get("Features", [])}
    cn_feats = {f["FeatureId"]: f for f in cn_data.get("Features", [])}
    fields = ["Label", "ToolTip", "ApplyText", "UndoLabel", "ApplyUndoText"]
    residual = {f: [] for f in fields}
    for fid, en_f in en_feats.items():
        cn_f = cn_feats.get(fid)
        if not cn_f:
            continue
        for field in fields:
            en_text = (en_f.get(field) or "").strip()
            cn_text = (cn_f.get(field) or "").strip()
            if not en_text:
                continue
            if not cn_text or en_text == cn_text:
                residual[field].append(fid)
    return residual

def validate_identifiers(en_path, cn_path):
    en_data = json.load(open(en_path, "r", encoding="utf-8-sig"))
    cn_data = json.load(open(cn_path, "r", encoding="utf-8-sig"))
    errors = []
    if [f["FeatureId"] for f in en_data.get("Features", [])] != [f["FeatureId"] for f in cn_data.get("Features", [])]:
        errors.append("FeatureId mismatch")
    if [c["Name"] for c in en_data.get("Categories", [])] != [c["Name"] for c in cn_data.get("Categories", [])]:
        errors.append("Category.Name translated")
    if [f.get("Category") for f in en_data.get("Features", [])] != [f.get("Category") for f in cn_data.get("Features", [])]:
        errors.append("Feature.Category modified")
    if [g["GroupId"] for g in en_data.get("UiGroups", [])] != [g["GroupId"] for g in cn_data.get("UiGroups", [])]:
        errors.append("UiGroup GroupId modified")
    return errors

def norm_aid(aid):
    if isinstance(aid, list):
        return aid[0]
    return aid

def validate_apps(en_path, cn_path):
    en_data = json.load(open(en_path, "r", encoding="utf-8-sig"))
    cn_data = json.load(open(cn_path, "r", encoding="utf-8-sig"))
    errors = []
    en_apps = {norm_aid(a["AppId"]): a for a in en_data.get("Apps", [])}
    cn_apps = {norm_aid(a["AppId"]): a for a in cn_data.get("Apps", [])}
    untranslated = []
    for aid, en_a in en_apps.items():
        cn_a = cn_apps.get(aid)
        if not cn_a:
            continue
        en_desc = (en_a.get("Description") or "").strip()
        cn_desc = (cn_a.get("Description") or "").strip()
        if en_desc and (not cn_desc or en_desc == cn_desc):
            untranslated.append(aid)
    if untranslated:
        errors.append(f"Apps.json Description untranslated: {len(untranslated)}")
    for app in cn_data.get("Apps", []):
        for field in ("FriendlyName", "AppId"):
            val = app.get(field, "")
            if isinstance(val, list):
                val = val[0]
            if isinstance(val, str) and any(ord(c) > 127 for c in val):
                errors.append(f"Apps.json {field} translated: {val}")
    return errors

def run(source_dir, output_dir):
    en_feat = Path(source_dir) / "Config" / "Features.json"
    cn_feat = Path(output_dir) / "Config" / "Features.json"
    cn_apps = Path(output_dir) / "Config" / "Apps.json"
    cn_def = Path(output_dir) / "Config" / "DefaultSettings.json"
    en_apps = Path(source_dir) / "Config" / "Apps.json"
    all_ok = True

    print("-- BOM --")
    for name, p in [("Features.json", cn_feat), ("Apps.json", cn_apps), ("DefaultSettings.json", cn_def)]:
        ok = has_bom(p)
        print(f"  {name}: {'OK' if ok else 'MISSING'}")
        if not ok:
            all_ok = False

    print("\n-- Identifiers --")
    ie = validate_identifiers(en_feat, cn_feat)
    if ie:
        for e in ie:
            print(f"  FAIL: {e}")
        all_ok = False
    else:
        print("  OK: all identifiers intact")

    print("\n-- Translation Coverage --")
    residual = validate_residual(en_feat, cn_feat)
    total = 0
    for field, ids in residual.items():
        if ids:
            print(f"  UNTRANSLATED {field}: {len(ids)}")
            total += len(ids)
    if total == 0:
        print("  OK: all fields translated")
    else:
        all_ok = False

    print("\n-- Apps.json --")
    ae = validate_apps(en_apps, cn_apps)
    if ae:
        for e in ae:
            print(f"  FAIL: {e}")
        all_ok = False
    else:
        print("  OK: Description translated, identifiers intact")

    print("\n-- Counts --")
    enf = len(json.load(open(en_feat, "r", encoding="utf-8-sig")).get("Features", []))
    cnf = len(json.load(open(cn_feat, "r", encoding="utf-8-sig")).get("Features", []))
    ena = len(json.load(open(en_apps, "r", encoding="utf-8-sig")).get("Apps", []))
    cna = len(json.load(open(cn_apps, "r", encoding="utf-8-sig")).get("Apps", []))
    print(f"  Features: EN {enf} = CN {cnf} {'OK' if enf == cnf else 'FAIL'}")
    print(f"  Apps:     EN {ena} = CN {cna} {'OK' if ena == cna else 'FAIL'}")
    if enf != cnf or ena != cna:
        all_ok = False

    print(f"\n{'=' * 32}")
    print("ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED")
    return all_ok

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    ok = run(a.source, a.output)
    sys.exit(0 if ok else 1)
