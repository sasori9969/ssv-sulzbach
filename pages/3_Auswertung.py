import streamlit as st
import pandas as pd
from utils import load_competitions, load_participants

st.title("Auswertung")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "results" in participants:
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))

    if st.button("Auswertung anzeigen"):
        if selected_competition:
            results = participants["results"].get(selected_competition, {})

            # Einzelwertung
            st.subheader("Einzelwertung")
            individual_results = []
            for shooter, result in results.items():
                individual_results.append({"Name": shooter, "Ergebnis": result})
            df_individual = pd.DataFrame(individual_results)
            df_individual = df_individual.sort_values(by="Ergebnis", ascending=False)
            df_individual.insert(0, "Platz", range(1, len(df_individual) + 1))
            st.dataframe(df_individual.set_index("Platz"))  # Index-Spalte ausblenden

            # Mannschaftswertung
            st.subheader("Mannschaftswertung")
            team_results = {}
            for shooter, result in results.items():
                for team in participants["shooters"][shooter]["teams"]:
                    if team not in team_results:
                        team_results[team] = []
                    team_results[team].append(result)

            # Summe der Mannschaftsergebnisse berechnen
            sum_team_results = []
            for team, team_results_list in team_results.items():
                sum_team_results.append({"Mannschaft": team, "Ergebnis": sum(team_results_list)})
            df_team = pd.DataFrame(sum_team_results)
            df_team = df_team.sort_values(by="Ergebnis", ascending=False)
            df_team.insert(0, "Platz", range(1, len(df_team) + 1))
            st.dataframe(df_team.set_index("Platz"))  # Index-Spalte ausblenden

        else:
            st.error("Bitte Wettbewerb auswählen.")
else:
    st.warning("Bitte erst Ergebnisse eingeben.")