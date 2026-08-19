# Quaranta Crediti

A minimal retro arcade leaderboard for two friends. Hugo static site, hosted on GitHub Pages.

## What it is

Every month a classic arcade game is chosen, each player gets 40 credits, and the
highest score wins. Scores are submitted through GitHub Issues (with a photo or
screenshot as proof) and the leaderboard updates automatically via a GitHub Action.

- Site language: Italian
- Fonts: Press Start 2P (display), IBM Plex Mono (body), both self-hosted under `static/fonts/`
- No build-time external dependencies, no CDN

## Structure

```
salagiochi/
├── data/scores.yml                 # leaderboard data (source of truth)
├── content/
│   ├── _index.md                   # home: intro, rules
│   └── submit.md                   # score submission page (uses layouts/submit.html)
├── layouts/
│   ├── _default/baseof.html        # html shell, header marquee, footer
│   ├── index.html                  # renders the leaderboards from data
│   ├── submit.html                 # score submission form
│   └── partials/game-card.html     # renders one game's score table
├── static/
│   ├── css/arcade.css              # retro CRT theme
│   ├── js/submit.js                # builds the pre-filled GitHub issue URL
│   └── fonts/                      # self-hosted woff2 fonts
├── scripts/update_scores.py        # parses issues and updates data/scores.yml
└── .github/
    ├── ISSUE_TEMPLATE/score.yml    # manual score issue template
    └── workflows/
        ├── pages.yml               # builds and deploys the site to Pages
        └── score-update.yml        # runs update_scores.py on new issues
```

## Local development

```sh
hugo server -D
```

Requires Hugo >= 0.162. The site builds with `hugo` into `public/`.

## Deployment

The site is published to GitHub Pages at
`https://aadm.github.io/salagiochi/`. Set it up from a fresh clone:

1. Install and authenticate the GitHub CLI (`gh auth login`).
2. Create the remote repo and push the current branch:

   ```sh
   gh repo create aadm/salagiochi --public --source=. --push
   ```

3. Enable GitHub Pages with the "GitHub Actions" source (the `pages` workflow
   deploys automatically on every push):

   ```sh
   gh api -X POST repos/aadm/salagiochi/pages \
     -f "build_type=workflow" --silent
   ```

   Alternatively, use the web UI: repo Settings -> Pages -> Source ->
   "GitHub Actions".

After a push, `pages.yml` builds the site and deploys it. The first deployment
takes a minute or two.

## How score submission works

1. A player fills the form on `/submit/`. The form opens a pre-filled GitHub issue
   at `https://github.com/aadm/salagiochi/issues/new?title=...&body=...`.
2. The player drags a photo or screenshot of the score into the issue body and
   submits the issue. Title format: `[PUNTEGGIO] <GIOCO> - <GIOCATORE>: <PUNTEGGIO>`.
3. The `score-update` workflow (triggered on `issues: opened` and `edited`) runs
   `scripts/update_scores.py`, which parses the body, validates the author against
   an allowlist, downloads the attached photo, reduces it (max 1600px, JPEG ~82),
   commits it to `static/proof/`, and upserts the entry into
   `data/scores.yml` with `proof` pointing at the local image.
4. The commit pushes to `main`, which triggers the `pages` workflow and redeploys
   the site. The leaderboard updates within a couple of minutes.

If the issue body has no photo, or the download fails, `proof` falls back to the
issue URL. Issue attachments are hosted on GitHub's CDN and never count against
the repository size; only the reduced local copy is committed.

### Score body format

The form-generated issue uses bold labels:

```markdown
**Gioco:** Mario Bros
**Punteggio:** 87400
**Giocatore:** strmnk
**Nota:** ultimo giorno
```

Manual issues through the issue template produce `### Gioco` headings; both are
parsed by `update_scores.py`.

## Configuration

- Repo URL and issue URL: `params.repo` and `params.repo_issues` in `hugo.yaml`.
- Score submission allowlist: `ALLOWED_AUTHORS` at the top of
  `scripts/update_scores.py`. Currently only `aadm`; add Fabio's GitHub username
  when you have it.

## Adding a game

Add a block at the top of `data/scores.yml` (the first block is the current game
of the month):

```yaml
- slug: pac-man
  name: Pac-Man
  platform: Arcade (Namco, 1980)
  year: 2026
  month: 9
  credits: 40
  entries: []
```

Optionally run `hugo new content content/<slug>.md` if you want a dedicated page.

## Manual score editing

The issue workflow is the normal path, but you can edit `data/scores.yml`
directly (even from the GitHub web UI). Each entry needs `player` (strmnk or
anal), `score` (integer), `date` (ISO), and `proof` (a GitHub issue URL or a
local photo path).

### Storing proof photos

Hugo copies `static/` files verbatim and does not resize anything. Save photos
under `static/proof/` (published at `/salagiochi/proof/...`) and reference them
with the path relative to the site root, **without** a leading slash:

```yaml
    entries:
      - player: strmnk
        score: 87400
        date: 2026-07-18
        proof: proof/mariobros-strmnk-2026-07-18.jpg
```

Photo sources differ a lot in size: an iPhone photo is typically 4000x3000 px
and several MB, an emulator screenshot (RetroArch) is 1920x1080 but a large PNG,
while an image passed through WhatsApp arrives already compressed. Downscale to a
max dimension of 1600 px and strip EXIF with the helper script:

```sh
python3 scripts/optimize_photo.py photo.jpg static/proof/mariobros-strmnk-2026-07-18.jpg
```

Requires Pillow. If you prefer ImageMagick:

```sh
convert photo.jpg -resize 1600x1600\> -strip -quality 82 static/proof/mariobros-strmnk-2026-07-18.jpg
```

## Workflows

- `pages.yml`: Hugo build + GitHub Pages deploy via `actions/deploy-pages`. Requires
  Pages source set to "GitHub Actions" in the repo settings.
- `score-update.yml`: parse score issues and commit the updated `data/scores.yml`.

## License

CC-BY-NC-ND