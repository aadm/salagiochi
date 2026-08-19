#!/usr/bin/env python3
"""Parse a score-submission GitHub issue and update data/scores.yml.

Run by .github/workflows/score-update.yml with env vars:
  ISSUE_NUMBER, ISSUE_TITLE, ISSUE_BODY, ISSUE_AUTHOR
  GITHUB_TOKEN, GITHUB_REPOSITORY
"""

import os
import re
import sys
from datetime import date

import yaml

DATA_FILE = "data/scores.yml"

# Only these GitHub users may submit scores.
# GitHub usernames allowed to open score issues (not display names).
# TODO: add the second player's GitHub username to this set.
ALLOWED_AUTHORS = {"aadm"}


def issue_comment(issue_number, body):
    import shutil
    import subprocess

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
    entries = target.setdefault("entries", [])
    updated = False
    for entry in entries:
        if entry["player"] == player:
            entry["score"] = score
            entry["date"] = today
            entry["proof"] = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/issues/{issue_number}"
            updated = True
            break
    if not updated:
        entries.append(
            {
                "player": player,
                "score": score,
                "date": today,
                "proof": f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/issues/{issue_number}",
            }
        )

    save_games(data)

    try:
        import subprocess

        subprocess.run(["git", "config", "user.name", "scorebot"], check=True)
        subprocess.run(
            ["git", "config", "user.email", "scorebot@users.noreply.github.com"],
            check=True,
        )
        subprocess.run(["git", "add", DATA_FILE], check=True)
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
                f"https://x-access-token:{os.environ['GITHUB_TOKEN']}@github.com/{os.environ['GITHUB_REPOSITORY']}.git",
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