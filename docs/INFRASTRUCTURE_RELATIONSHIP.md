# How This Book Becomes a Website

This document describes how `ice-cream-book` relates to its companion repository, [`PitziLabs/foundry-platform-demo`](https://github.com/PitziLabs/foundry-platform-demo), which turns these recipes into a live website at **icecreamtofightwith.com**.

## This Repo's Role

`ice-cream-book` is the **content source of truth**. Every recipe, the front matter, the back matter, and the style guide all live here as plain Markdown files. This repo knows nothing about AWS, Docker, or web frameworks — it is purely editorial.

The key content that flows downstream:

```
recipes/
├── 01_coconut_pandan.md
├── 02_sinh_to_bo.md
├── ...
└── 28_appalachian_pawpaw_maple.md
```

Each recipe file follows a consistent structure — H1 title, italic subtitle, difficulty tier, total time, ingredient list, numbered steps, and notes — that the infrastructure side depends on for automated parsing.

## What Happens to the Content

The `foundry-platform-demo` repo contains a script called `sync_recipes.py` that reads these Markdown files and transforms them into web-ready content:

```
ice-cream-book/recipes/*.md
        │
        ▼
  sync_recipes.py (in foundry-platform-demo)
        │  - Extracts title, subtitle, difficulty tier, total time
        │  - Generates YAML frontmatter for Astro
        │  - Writes to src/content/recipes/
        ▼
  Astro static site build → nginx container → ECS Fargate → icecreamtofightwith.com
```

In CI/CD, the `RECIPE_SOURCE` environment variable points `sync_recipes.py` at this repo's recipe files. For local development, the script defaults to `../ice-cream-book/recipes/`, expecting both repos to be cloned as siblings.

## What the Infrastructure Expects from Us

The parsing in `sync_recipes.py` relies on specific conventions in our recipe files:

| Convention | What Gets Parsed | Example |
|-----------|-----------------|---------|
| First `# ` line | Recipe title | `# Coconut Pandan` |
| First `*italic*` line | Subtitle | `*Southeast Asian dessert meets churned custard*` |
| `**Difficulty:**` line | Tier + description | `**Difficulty:** Legit - Coconut milk requires attention` |
| `**Total Time:**` line | Time estimate | `**Total Time:** 5-6 hours (including chill time)` |
| Filename pattern `##_name.md` | Recipe number + URL slug | `01_coconut_pandan.md` → recipe #1, slug `01_coconut_pandan` |

Breaking these conventions will cause the website to display missing or incorrect metadata. The recipe body (everything after the Total Time line) is passed through as-is.

## What Changes Here Affect the Website

- **Editing a recipe** — Content updates flow through on the next site build. No infra changes needed.
- **Adding a new recipe** — Create a new numbered `.md` file in `recipes/`. The sync script auto-discovers all `*.md` files in the directory.
- **Renaming a recipe file** — Changes the URL slug on the website. Old URLs will 404 unless redirects are added on the infra side.
- **Changing the format** — If the H1, italic subtitle, `**Difficulty:**`, or `**Total Time:**` patterns change, `sync_recipes.py` must be updated in `foundry-platform-demo` to match.

## What Does NOT Affect the Website

- `front_matter/` and `back_matter/` — These are used by `compile_book.py` to produce the complete book document but are **not** consumed by the website.
- `STYLE_GUIDE.md`, `CLAUDE.md`, `_typos.toml` — Editorial tooling only.
- `compile_book.py` / `compile_book.sh` — These compile the full book into a single Markdown file. The website uses a completely separate build pipeline.

## Local Development Setup

To work on both repos together locally:

```
~/projects/
├── ice-cream-book/        # this repo
└── foundry-platform-demo/
    └── app/
        └── ice_cream_site/
            └── sync_recipes.py   # expects ../ice-cream-book/recipes/
```

With this layout, running `python sync_recipes.py` from the `ice_cream_site` directory will pull recipes directly from your local `ice-cream-book` checkout.
