import json

def save_competitions(competitions):
    with open("competitions.json", "w") as f:
        json.dump(competitions, f, indent=4)

def load_competitions():
    try:
        with open("competitions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_participants(participants):
    with open("participants.json", "w") as f:
        json.dump(participants, f, indent=4)

def load_participants():
    try:
        with open("participants.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}