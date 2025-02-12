import streamlit as st
import json
import os

# Datei zur Speicherung der Daten
DATA_FILE = "schuetzen_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
                data.setdefault("schuetzen", {})
                data.setdefault("teams", {})
                data.setdefault("ergebnisse", {})
                if not isinstance(data["schuetzen"], dict):
                    data["schuetzen"] = {}
                return data
            except json.JSONDecodeError:
                return {"schuetzen": {}, "teams": {}, "ergebnisse": {}}
    return {"schuetzen": {}, "teams": {}, "ergebnisse": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

st.title("Schützenwettbewerb Verwaltung")

# Schützen eingeben
st.header("Schützen hinzufügen")
vorname = st.text_input("Vorname")
nachname = st.text_input("Nachname")
als_einzelstarter = st.checkbox("Als Einzelstarter anmelden")
if st.button("Schützen hinzufügen"):
    schuetze = f"{vorname} {nachname}"
    if schuetze and schuetze not in data["schuetzen"]:
        data["schuetzen"][schuetze] = {"einzelstarter": als_einzelstarter}
        save_data(data)
        st.success(f"{schuetze} hinzugefügt!")

# Teams verwalten
st.header("Teams verwalten")
team_name = st.text_input("Teamname")
selected_schuetzen = st.multiselect("Schützen dem Team hinzufügen", list(data.get("schuetzen", {}).keys()))
if st.button("Team speichern"):
    if team_name:
        data["teams"][team_name] = selected_schuetzen
        save_data(data)
        st.success(f"Team {team_name} gespeichert!")

# Ergebnisse erfassen
st.header("Ergebnisse eintragen")
schuetze = st.selectbox("Schütze auswählen", list(data.get("schuetzen", {}).keys()))
ergebnis = st.number_input("Ergebnis eingeben", min_value=0)
teams = [team for team, schuetzen in data.get("teams", {}).items() if schuetze in schuetzen]
teams.append("Einzelwertung") if data["schuetzen"].get(schuetze, {}).get("einzelstarter", False) else None
selected_team = st.selectbox("Team auswählen", teams)
if st.button("Ergebnis speichern"):
    if schuetze not in data["ergebnisse"]:
        data["ergebnisse"][schuetze] = {}
    data["ergebnisse"][schuetze][selected_team] = ergebnis
    save_data(data)
    st.success(f"Ergebnis für {schuetze} gespeichert!")

# Beste Einzelwertung berechnen
def beste_einzelwertung(schuetze):
    if schuetze in data["ergebnisse"]:
        return max(data["ergebnisse"][schuetze].values(), default=0)
    return 0

# Ergebnisse anzeigen
st.header("Ergebnisse Übersicht")

st.subheader("Einzelergebnisse")
for schuetze in data.get("schuetzen", {}).keys():
    st.write(f"{schuetze}: {beste_einzelwertung(schuetze)} Punkte")

st.subheader("Teamergebnisse")
team_scores = {team: 0 for team in data.get("teams", {})}
for schuetze, ergebnisse in data.get("ergebnisse", {}).items():
    for team, score in ergebnisse.items():
        if team != "Einzelwertung":
            team_scores[team] += score
for team, score in team_scores.items():
    st.write(f"{team}: {score} Punkte")

# Bearbeiten und Löschen von Schützen und Teams
st.header("Datenverwaltung")

delete_schuetze = st.selectbox("Schützen löschen", [""] + list(data.get("schuetzen", {}).keys()))
if st.button("Schütze entfernen") and delete_schuetze:
    data["schuetzen"].pop(delete_schuetze, None)
    data["ergebnisse"].pop(delete_schuetze, None)
    for team in data["teams"]:
        if delete_schuetze in data["teams"][team]:
            data["teams"][team].remove(delete_schuetze)
    save_data(data)
    st.success(f"{delete_schuetze} wurde entfernt!")

delete_team = st.selectbox("Team löschen", [""] + list(data.get("teams", {}).keys()))
if st.button("Team entfernen") and delete_team:
    data["teams"].pop(delete_team, None)
    save_data(data)
    st.success(f"Team {delete_team} wurde entfernt!")

# Ergebnisse bearbeiten
st.header("Ergebnisse bearbeiten")
edit_schuetze = st.selectbox("Schütze auswählen", [""] + list(data.get("schuetzen", {}).keys()))
if edit_schuetze:
    edit_team = st.selectbox("Team auswählen", [""] + list(data.get("ergebnisse", {}).get(edit_schuetze, {}).keys()))
    if edit_team:
        new_score = st.number_input("Neues Ergebnis eingeben", min_value=0, value=data["ergebnisse"][edit_schuetze][edit_team])
        if st.button("Ergebnis aktualisieren"):
            data["ergebnisse"][edit_schuetze][edit_team] = new_score
            save_data(data)
            st.success(f"Ergebnis für {edit_schuetze} im Team {edit_team} aktualisiert!")

if st.button("Daten zurücksetzen"):
    data = {"schuetzen": {}, "teams": {}, "ergebnisse": {}}
    save_data(data)
    st.success("Alle Daten wurden zurückgesetzt!")
