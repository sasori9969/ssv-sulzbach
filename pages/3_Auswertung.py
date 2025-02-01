import streamlit as st
import json
from utils import load_competitions, load_participants  # Importiere die Funktionen

st.title("Auswertung")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "results" in participants:  # Sicherstellen, dass Daten vorhanden sind
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))

    if st.button("Auswertung anzeigen"):
        if selected_competition:
            results = participants["results"].get(selected_competition, {})

            # Einzelwertung
            st.subheader("Einzelwertung")
            individual_results = {}
            for shooter, result in results.items():
                individual_results[shooter] = result  # Hier könnte man das beste Ergebnis berücksichtigen
            st.dataframe(individual_results)  # Anzeige als DataFrame

            # Mannschaftswertung
            st.subheader("Mannschaftswertung")
            team_results = {}
            for shooter, result in results.items():
                for team in participants["shooters"][shooter]["teams"]:
                    if team not in team_results:
                        team_results[team] = []
                    team_results[team].append(result)

            # Durchschnittliche Mannschaftsergebnisse berechnen
            average_team_results = {}
            for team, team_results_list in team_results.items():
                average_team_results[team] = sum(team_results_list) / len(team_results_list) if team_results_list else 0
            st.dataframe(average_team_results)  # Anzeige als DataFrame
        else:
            st.error("Bitte Wettbewerb auswählen.")
else:
    st.warning("Bitte erst Ergebnisse eingeben.")