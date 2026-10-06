#!/usr/bin/env python3
"""Check GAME TIMES for a clickable SACRAMENTO link and notify ntfy once."""
import json, os, sys
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

PAGE_URL = "https://allstartournaments.com/fastpitch/black-widow/"
STATE_PATH = "state.json"
DEFAULT_TOPIC = "https://ntfy.sh/blackwidow-sac"

class GameTimesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_game_times = False
        self.heading_tag = None
        self.anchor_hrefs = []
        self.matches = []
    def handle_starttag(self, tag, attrs):
        if tag in {"h1","h2","h3","h4","h5","h6"}:
            self.heading_tag = tag
        if tag == "a" and self.in_game_times:
            self.anchor_hrefs.append(dict(attrs).get("href"))
    def handle_endtag(self, tag):
        if tag == "a" and self.anchor_hrefs:
            self.anchor_hrefs.pop()
        if tag == self.heading_tag:
            self.heading_tag = None
            self.in_game_times = False
    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        upper = text.upper()
        if self.heading_tag and "GAME TIMES" in upper:
            self.in_game_times = True
        elif self.in_game_times and "SACRAMENTO" in upper and self.anchor_hrefs:
            self.matches.append(self.anchor_hrefs[-1])

def fetch_html():
    request = Request(PAGE_URL, headers={"User-Agent": "sacramento-game-times-monitor/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")

def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as handle:
            value = json.load(handle)
            return value if isinstance(value, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_state(state):
    with open(STATE_PATH + ".tmp", "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(STATE_PATH + ".tmp", STATE_PATH)

def send_notification(destination):
    topic = os.environ.get("NTFY_TOPIC", DEFAULT_TOPIC)
    payload = f"SACRAMENTO game time is now clickable:\n{destination}".encode()
    request = Request(topic, data=payload, method="POST", headers={
        "Content-Type": "text/plain; charset=utf-8",
        "Title": "Sacramento game time available",
        "Priority": "high",
        "Tags": "calendar",
    })
    with urlopen(request, timeout=30) as response:
        if response.status >= 300:
            raise RuntimeError(f"ntfy returned HTTP {response.status}")

def main():
    parser = GameTimesParser()
    parser.feed(fetch_html())
    destination = urljoin(PAGE_URL, parser.matches[0]) if parser.matches else None
    state = load_state()
    if destination:
        print(f"Clickable SACRAMENTO link found: {destination}")
        if not state.get("alerted"):
            send_notification(destination)
            save_state({"alerted": True, "destination": destination})
            print("Notification sent.")
        else:
            print("Already notified; no notification sent.")
    else:
        print("No clickable SACRAMENTO link found in GAME TIMES.")
        if state.get("alerted"):
            save_state({"alerted": False})
            print("Alert state reset.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Monitor failed: {exc}", file=sys.stderr)
        raise
