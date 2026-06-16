
#!/usr/bin/env python3
"""Win11Debloat i18n pipeline. Usage: python cli.py zh-CN [-r Win11Debloat-cn-old]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline.extract import run as extract_run
from pipeline.translate import run as translate_run
from pipeline.assemble import run as assemble_run
from pipeline.validate import run as validate_run

def main():
    import argparse
    p = argparse.ArgumentParser(description="Win11Debloat i18n pipeline")
    p.add_argument("lang", help="Language code (e.g. zh-CN)")
    p.add_argument("-s", "--source", type=Path, default=Path("Win11Debloat"), help="Source dir")
    p.add_argument("-o", "--output", type=Path, default=None, help="Output dir")
    p.add_argument("-r", "--reference", type=Path, default=None, help="Reference translation dir")
    p.add_argument("--skip-validate", action="store_true")
    a = p.parse_args()

    root = Path(__file__).resolve().parent
    lang_dir = root / "languages" / a.lang
    if not lang_dir.is_dir():
        langs = [d.name for d in (root / "languages").iterdir() if d.is_dir()] if (root / "languages").is_dir() else []
        print(f"Unknown language: {a.lang}. Available: {', '.join(langs)}")
        sys.exit(1)

    source = a.source.resolve()
    if not (source / "Config" / "Features.json").exists():
        print(f"Invalid source: {source}")
        sys.exit(1)

    output = a.output or Path(f"Win11Debloat-{a.lang.replace('-CN','').replace('-cn','')}")
    output = output.resolve()
    tmp = root / ".pipeline-temp"
    tmp.mkdir(exist_ok=True)
    units_f = tmp / f"units-{a.lang}.json"
    trans_f = tmp / f"translated-{a.lang}.json"

    print("=" * 50)
    print("Step 1/4: Extract")
    print("=" * 50)
    extract_run(source, units_f)

    print(f"\n{'=' * 50}")
    print("Step 2/4: Translate")
    print("=" * 50)
    translate_run(units_f, lang_dir, trans_f, a.reference)

    print(f"\n{'=' * 50}")
    print("Step 3/4: Assemble")
    print("=" * 50)
    assemble_run(source, trans_f, output)

    ok = True
    if not a.skip_validate:
        print(f"\n{'=' * 50}")
        print("Step 4/4: Validate")
        print("=" * 50)
        ok = validate_run(source, output)

    print(f"\n{'=' * 50}")
    print("Done")
    print("=" * 50)
    print(f"  Language: {a.lang}")
    print(f"  Output:   {output}")
    print(f"  Checks:   {'PASS' if ok else 'FAIL'}")
    print(f"\nDeploy:")
    print(f"  .\\\\{output.name}\\\\Win11Debloat.ps1")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
