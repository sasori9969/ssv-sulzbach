import streamlit as st
import pandas as pd
import time
from utils import load_competitions, load_participants

st.title("Auswertung")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "results" in participants and "shooters" in participants:  # Check for "shooters"
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))

    if "is_saving" not in st.session_state:
        st.session_state.is_saving = False

    if st.button("Auswertung anzeigen"):
        if selected_competition:
            results = participants["results"].get(selected_competition, {})

            if results:
                # Einzelwertung
                st.subheader("Einzelwertung")
                individual_results = [{"Name": shooter, "Ergebnis": result} for shooter, result in results.items()]
                df_individual = pd.DataFrame(individual_results)
                df_individual = df_individual.sort_values(by="Ergebnis", ascending=False)
                df_individual.insert(0, "Platz", range(1, len(df_individual) + 1))
                st.dataframe(df_individual.set_index("Platz"))

                # Mannschaftswertung
                st.subheader("Mannschaftswertung")
                team_results = {}
                for shooter, result in results.items():
                    for team in participants["shooters"].get(shooter, {}).get("teams", []):  # Handle missing teams
                        team_results.setdefault(team, []).append(result)  # More efficient

                sum_team_results = [{"Mannschaft": team, "Ergebnis": sum(results)} for team, results in team_results.items()]
                df_team = pd.DataFrame(sum_team_results)
                df_team = df_team.sort_values(by="Ergebnis", ascending=False)
                df_team.insert(0, "Platz", range(1, len(df_team) + 1))
                st.dataframe(df_team.set_index("Platz"))
            else:
                st.warning(f"Keine Ergebnisse für {selected_competition} gefunden.")

        else:
            st.error("Bitte Wettbewerb auswählen.")

    if st.button("Speichern", disabled=st.session_state.is_saving):
        if not st.session_state.is_saving:
            st.session_state.is_saving = True
            with st.spinner("Speichere Daten..."): # Ladeindikator
                # Hier kommt der Code zum Speichern der Daten hin...
                time.sleep(2)  # Simuliere Speichervorgang (2 Sekunden)
                st.success("Daten erfolgreich gespeichert!")
            time.sleep(2)  # 2 Sekunden Sperre nach der Meldung
            st.session_state.is_saving = False

else:
    st.warning("Bitte erst Ergebnisse und Teilnehmerdaten eingeben.")  # More informative message