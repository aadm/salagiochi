# AGENTS.md

Project-specific conventions for this repository.

## Overview

"Quaranta Crediti" is a Hugo static site (Italian language) hosting an arcade
leaderboard for two players. Scores are stored in `data/scores.yml` and are
updated automatically from GitHub Issues by `.github/workflows/score-update.yml`.

## Commands

- Build: `hugo` (outputs to `public/`)
- Dev server: `hugo server -D`
- Hugo version: >= 0.162. No extended features are used.

## Conventions

- Site-facing text must be in Italian. Code, commit messages, and docs are in
  English.
- Leaderboard data lives only in `data/scores.yml`. The first `games` entry is the
  current game of the month; the rest are the archive.
- Score entries need: `player` (strmnk or anal), `score` (integer), `date` (ISO),
  `proof` (GitHub issue URL, or a local path under `static/proof/` written without
  a leading slash, e.g. `proof/pooyan-strmnk-2026-08-17.jpg`). The photo is
  optional: without one, the issue URL is the proof.
- Proof photos go in `static/proof/` and must be downscaled first
  (`scripts/optimize_photo.py`, max ~1600px, JPEG ~82); Hugo copies static files
  verbatim and does not resize them. Issue submissions are reduced automatically
  by `update_scores.py` (download via the workflow token, reduce, commit); only
  the reduced copy is stored in the repo.
- Self-host all assets under `static/`; do not introduce CDN dependencies.
- The score-update script is the source of truth for how issues map to data; keep
  `scripts/update_scores.py` and `data/scores.yml` in sync.
- `ALLOWED_AUTHORS` in `scripts/update_scores.py` whitelists who may submit scores;
  add Fabio's GitHub username when provided.

## GitHub Actions

- `pages.yml` deploys to GitHub Pages; repo must use Pages source "GitHub Actions".
- `score-update.yml` runs on issue open/edit; it needs the `issues: write` and
  `contents: write` permissions it already declares.

## Verification

- After changing templates or data, run `hugo` and check for warnings/errors.
- To exercise the score-update logic locally without a repo, run the module with
  env vars set and a throwaway `DATA_FILE` (see README).