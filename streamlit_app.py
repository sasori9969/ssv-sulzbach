import streamlit as st
import json
from utils import load_competitions, save_competitions  # Importiere die Funktionen

def save_competitions(competitions):
    with open("competitions.json", "w") as f:
        json.dump(competitions, f)

def load_competitions():
    try:
        with open("competitions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

st.title("Wettbewerbe verwalten")

competitions = load_competitions()

new_competition = st.text_input("Neuer Wettbewerb")
new_date = st.date_input("Datum")

if st.button("Wettbewerb hinzufügen"):
    competitions[new_competition] = str(new_date)
    save_competitions(competitions)
    st.success(f"Wettbewerb '{new_competition}' hinzugefügt.")

# Anzeige der vorhandenen Wettbewerbe
st.subheader("Vorhandene Wettbewerbe")
for competition, date in competitions.items():
    st.write(f"- {competition} ({date})")