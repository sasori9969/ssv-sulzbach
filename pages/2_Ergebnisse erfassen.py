import streamlit as st
import json
from utils import load_competitions, load_participants, save_participants  # Importiere die Funktionen

st.title("Ergebnisse eingeben")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "shooters" in participants:  # Sicherstellen, dass Daten vorhanden sind
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))
    selected_shooter = st.selectbox("Schützen auswählen", options=list(participants["shooters"].keys()))
    result = st.number_input("Ergebnis eingeben")

    if st.button("Ergebnis speichern"):
        if selected_competition and selected_shooter:
            if "results" not in participants:
                participants["results"] = {}
            if selected_competition not in participants["results"]:
                participants["results"][selected_competition] = {}
            participants["results"][selected_competition][selected_shooter] = result
            save_participants(participants)
            st.success(f"Ergebnis für '{selected_shooter}' im Wettbewerb '{selected_competition}' gespeichert.")
            st.rerun()
        else:
            st.error("Bitte Wettbewerb und Schützen auswählen.")
else:
    st.warning("Bitte erst Wettbewerbe und Schützen anlegen.")