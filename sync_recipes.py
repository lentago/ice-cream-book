#!/usr/bin/env python3
"""
Convert ice-cream-book recipe markdown files into Astro-compatible
content files with YAML frontmatter.

Recipe source is determined by:
  1. RECIPE_SOURCE environment variable (used in CI/CD)
  2. Fallback: ../ice-cream-book/recipes/ (local dev)

Writes to: src/content/recipes/*.md
"""

import re
import os
import sys
from pathlib import Path

# Accept recipe source from env var (CI) or default to relative path (local)
RECIPE_SOURCE = os.environ.get("RECIPE_SOURCE")
if RECIPE_SOURCE:
    REPO_RECIPES = Path(RECIPE_SOURCE)
else:
    REPO_RECIPES = Path(__file__).parent.parent / "ice-cream-book" / "recipes"

OUTPUT_DIR = Path(__file__).parent / "src" / "content" / "recipes"

TIER_MAP = {
    "CHILL": {"order": 1, "color": "#7ecfb3", "label": "CHILL"},
    "LEGIT": {"order": 2, "color": "#f2c94c", "label": "LEGIT"},
    "THE REAL DEAL": {"order": 3, "color": "#f2994a", "label": "THE REAL DEAL"},
    "A FUCKING ORDEAL": {"order": 4, "color": "#eb5757", "label": "A FUCKING ORDEAL"},
}


def parse_recipe(filepath):
    """Parse a recipe markdown file and extract metadata + body."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    metadata = {
        "title": "",
        "subtitle": "",
        "tier": "",
        "tier_order": 0,
        "tier_color": "",
        "difficulty_text": "",
        "total_time": "",
        "recipeSlug": filepath.stem,
        "recipe_number": 0,
    }

    # Extract recipe number from filename
    num_match = re.match(r"(\d+)_", filepath.name)
    if num_match:
        metadata["recipe_number"] = int(num_match.group(1))

    # Parse title: first H1
    for line in lines:
        if line.startswith("# "):
            metadata["title"] = line[2:].strip()
            break

    # Parse subtitle: first italic line
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            metadata["subtitle"] = stripped.strip("*").strip()
            break

    # Parse difficulty line
    for line in lines:
        if line.startswith("**Difficulty:**"):
            diff_text = line.replace("**Difficulty:**", "").strip()
            for tier_name in TIER_MAP:
                if diff_text.upper().startswith(tier_name):
                    metadata["tier"] = tier_name
                    metadata["tier_order"] = TIER_MAP[tier_name]["order"]
                    metadata["tier_color"] = TIER_MAP[tier_name]["color"]
                    break
            dash_idx = diff_text.find(" - ")
            if dash_idx >= 0:
                metadata["difficulty_text"] = diff_text[dash_idx + 3:].strip()
            break

    # Parse total time
    for line in lines:
        if line.startswith("**Total Time:**"):
            metadata["total_time"] = line.replace("**Total Time:**", "").strip()
            break

    # Build the body: everything after the Total Time line
    body_started = False
    body_lines = []
    skip_next_blank = False

    for i, line in enumerate(lines):
        if line.startswith("**Total Time:**"):
            body_started = True
            skip_next_blank = True
            continue
        if body_started:
            if skip_next_blank and line.strip() == "":
                skip_next_blank = False
                continue
            skip_next_blank = False
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    if body.endswith("---"):
        body = body[:-3].rstrip()

    return metadata, body


def generate_frontmatter(metadata):
    """Generate YAML frontmatter string."""
    def esc(s):
        return s.replace('"', '\\"')

    return f"""---
title: "{esc(metadata['title'])}"
subtitle: "{esc(metadata['subtitle'])}"
tier: "{esc(metadata['tier'])}"
tierOrder: {metadata['tier_order']}
tierColor: "{metadata['tier_color']}"
difficultyText: "{esc(metadata['difficulty_text'])}"
totalTime: "{esc(metadata['total_time'])}"
recipeSlug: "{metadata['recipeSlug']}"
recipeNumber: {metadata['recipe_number']}
---"""


def main():
    if not REPO_RECIPES.exists():
        print(f"Error: Recipe directory not found at {REPO_RECIPES}")
        print(f"  Set RECIPE_SOURCE env var or ensure ../ice-cream-book/recipes/ exists")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    recipe_files = sorted(REPO_RECIPES.glob("*.md"))
    print(f"Found {len(recipe_files)} recipe files in {REPO_RECIPES}")

    for filepath in recipe_files:
        metadata, body = parse_recipe(filepath)
        frontmatter = generate_frontmatter(metadata)
        output = f"{frontmatter}\n\n{body}\n"

        out_path = OUTPUT_DIR / filepath.name
        out_path.write_text(output, encoding="utf-8")
        print(f"  ✓ {filepath.name} → {metadata['title']} [{metadata['tier']}]")

    print(f"\nDone! {len(recipe_files)} recipes written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
