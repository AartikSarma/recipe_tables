#!/usr/bin/env python3
"""Zip trn-recipe/ into dist/trn-recipe.skill for upload to Claude."""
import pathlib
import zipfile

root = pathlib.Path(__file__).parent
src = root / "trn-recipe"
out = root / "dist" / "trn-recipe.skill"
out.parent.mkdir(exist_ok=True)

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for path in sorted(src.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            z.write(path, path.relative_to(root))
print(f"wrote {out}")
