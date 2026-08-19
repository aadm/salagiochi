#!/usr/bin/env python3
"""Parse a score-submission GitHub issue and update data/scores.yml.

Run by .github/workflows/score-update.yml with env vars:
  ISSUE_NUMBER, ISSUE_TITLE, ISSUE_BODY, ISSUE_AUTHOR
  GITHUB_TOKEN, GITHUB_REPOSITORY
"""

import os
import re
import subprocess
import sys
from datetime import date

import yaml

DATA_FILE = "data/scores.yml"
PHOTO_ROOT = "static/proof"

# Only these GitHub users may submit scores.
# GitHub usernames allowed to open score issues (not display names).
ALLOWED_AUTHORS = {"aadm", "febs"}


def issue_comment(issue_number, body):
    import shutil

    if shutil.which("gh") is None:
        print(f"gh not available; would comment on #{issue_number}: {body}")
        return
    subprocess.run(
        ["gh", "issue", "comment", str(issue_number), "--body", body],
        check=False,
    )


def parse_field(body, label):
    bold = re.search(r"\*\*%s:\*\*\s*(.+?)\s*$" % re.escape(label), body, re.M)
    if bold:
        return bold.group(1).strip()

    heading = re.search(r"^###\s+%s\s*$" % re.escape(label), body, re.M)
    if heading:
        rest = body[heading.end():].splitlines()
        for line in rest:
            line = line.strip()
            if line:
                return line
    return None


def extract_score(raw):
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        raise ValueError("missing numeric score")
    return int(digits)


def extract_image_url(body):
    m = re.search(r"!\[[^\]]*\]\(([^)]+)\)", body or "")
    return m.group(1).strip() if m else None


def download_image(url, token, dest):
    """Download url to dest, handling GitHub's auth-gated attachment redirect.

    Attachments uploaded to issues live at github.com/user-attachments/assets/
    and 302 to a signed CDN URL only when the request carries a token; the token
    must NOT be forwarded to the CDN host. user-images.githubusercontent.com
    URLs are public and fetched directly.
    """
    if "user-attachments" in url:
        headers = subprocess.run(
            ["curl", "-s", "-D", "-", "-o", "/dev/null", "-H", f"Authorization: Bearer {token}", url],
            capture_output=True,
            text=True,
            check=True,
        )
        location = None
        for line in headers.stdout.splitlines():
            if line.lower().startswith("location:"):
                location = line.split(":", 1)[1].strip()
                break
        if location:
            subprocess.run(["curl", "-sfL", "-o", dest, location], check=True)
        else:
            subprocess.run(
                ["curl", "-sfL", "-o", dest, "-H", f"Authorization: Bearer {token}", url],
                check=True,
            )
    else:
        subprocess.run(["curl", "-sfL", "-o", dest, url], check=True)


def reduce_image(dest):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from optimize_photo import reduce_image as _reduce

    _reduce(dest, dest)


def load_games():
    with open(DATA_FILE, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {"games": []}


def save_games(data):
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        yaml.safe_dump(
            data,
            fh,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        )


def main():
    issue_number = os.environ.get("ISSUE_NUMBER")
    issue_title = os.environ.get("ISSUE_TITLE", "")
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_author = os.environ.get("ISSUE_AUTHOR", "")
    token = os.environ.get("GITHUB_TOKEN", "")

    if not issue_number:
        print("No ISSUE_NUMBER provided; nothing to do.")
        return 0

    if issue_author not in ALLOWED_AUTHORS:
        msg = f"Autore non autorizzato ({issue_author}): niente punteggio."
        print(msg)
        issue_comment(issue_number, msg)
        return 0

    game_name = parse_field(issue_body, "Gioco") or parse_field(issue_body, "Game")
    raw_score = parse_field(issue_body, "Punteggio") or parse_field(issue_body, "Score")
    player = parse_field(issue_body, "Giocatore") or parse_field(issue_body, "Player")

    # fallback to the issue title: [PUNTEGGIO] Game - player: score
    if not (game_name and raw_score and player):
        m = re.search(r"\[PUNTEGGIO\]\s*(.+?)\s*-\s*(.+?)\s*:\s*(.+)", issue_title)
        if m:
            game_name = game_name or m.group(1).strip()
            player = player or m.group(2).strip()
            raw_score = raw_score or m.group(3).strip()

    if not (game_name and raw_score and player):
        msg = "Impossibile leggere il punteggio. Uso il formato: **Gioco:**, **Punteggio:**, **Giocatore:**."
        print(msg)
        issue_comment(issue_number, msg)
        return 1

    try:
        score = extract_score(raw_score)
    except ValueError:
        msg = "Punteggio non numerico: non posso aggiornare la classifica."
        print(msg)
        issue_comment(issue_number, msg)
        return 1

    data = load_games()
    games = data.get("games", [])

    def norm(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())

    target = None
    for game in games:
        if norm(game["name"]) == norm(game_name):
            target = game
            break

    if target is None:
        msg = f"Gioco sconosciuto: {game_name}. Non posso aggiornare la classifica."
        print(msg)
        issue_comment(issue_number, msg)
        return 1

    today = date.today().isoformat()
    slug = target.get("slug") or re.sub(r"[^a-z0-9]+", "-", target["name"].lower()).strip("-")
    issue_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/issues/{issue_number}"

    proof = issue_url
    image_url = extract_image_url(issue_body)
    if image_url:
        dest = os.path.join(PHOTO_ROOT, f"{slug}-{player}-{today}.jpg")
        os.makedirs(PHOTO_ROOT, exist_ok=True)
        try:
            download_image(image_url, token, dest)
            reduce_image(dest)
            proof = os.path.join("proof", f"{slug}-{player}-{today}.jpg")
            print(f"stored reduced proof: {proof}")
        except Exception as exc:
            print(f"photo download/reduce failed, keeping issue link: {exc}")
            proof = issue_url

    entries = target.setdefault("entries", [])
    updated = False
    for entry in entries:
        if entry["player"] == player:
            entry["score"] = score
            entry["date"] = today
            entry["proof"] = proof
            updated = True
            break
    if not updated:
        entries.append(
            {
                "player": player,
                "score": score,
                "date": today,
                "proof": proof,
            }
        )

    save_games(data)

    try:
        subprocess.run(["git", "config", "user.name", "scorebot"], check=True)
        subprocess.run(
            ["git", "config", "user.email", "scorebot@users.noreply.github.com"],
            check=True,
        )
        subprocess.run(["git", "add", DATA_FILE, PHOTO_ROOT], check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"scorebot: {player} - {target['name']} {score} (#{issue_number})",
            ],
            check=False,
        )
        subprocess.run(
            [
                "git",
                "remote",
                "set-url",
                "origin",
                f"https://x-access-token:{token}@github.com/{os.environ['GITHUB_REPOSITORY']}.git",
            ],
            check=True,
        )
        subprocess.run(["git", "push", "origin", "HEAD"], check=True)
    except subprocess.CalledProcessError as exc:
        print(f"git step failed (probably nothing to commit): {exc}")

    msg = f"Classifica aggiornata: {player} - {target['name']} {score}."
    print(msg)
    issue_comment(issue_number, msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())