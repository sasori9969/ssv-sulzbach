import streamlit as st
import json
from utils import load_competitions, load_participants, save_participants

st.title("Ergebnisse eingeben")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "shooters" in participants:
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
            st.rerun()  # Seite neu laden, um die Tabelle zu aktualisieren
        else:
            st.error("Bitte Wettbewerb und Schützen auswählen.")

    # Ergebnistabelle anzeigen
    st.subheader("Ergebnisse")
    if "results" in participants and selected_competition in participants["results"]:
        results_table = participants["results"][selected_competition]
        sorted_shooters = sorted(results_table.keys(), key=lambda x: results_table[x], reverse=True)  # Sortieren nach Ergebnis absteigend
        for shooter in sorted_shooters:
            result = results_table[shooter]
            col1, col2, col3 = st.columns(3)  # Spalten für Layout
            with col1:
                st.write(shooter)
            with col2:
                new_result = st.number_input("Ergebnis", value=result, key=f"{selected_competition}-{shooter}")  # Eindeutiger Key für jedes Eingabefeld
            with col3:
                if st.button("Ändern", key=f"change-{selected_competition}-{shooter}"):
                    participants["results"][selected_competition][shooter] = new_result
                    save_participants(participants)
                    st.success("Ergebnis geändert.")
                    st.rerun()  # Seite neu laden, um die Tabelle zu aktualisieren
    else:
        st.info("Noch keine Ergebnisse für diesen Wettbewerb.")

else:
    st.warning("Bitte erst Wettbewerbe und Schützen anlegen.")