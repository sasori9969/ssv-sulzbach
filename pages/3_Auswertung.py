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
# --- Mannschaftswertung (überarbeitet) ---
            st.subheader("Mannschaftswertung")
            team_results = {}
            for result_key, result_value in results.items():
                parts = result_key.split("-")
                shooter = parts[0]
                context_type = parts[1]
                context_name = "-".join(parts[2:]) if len(parts) > 2 else None
                if context_type == "team":
                    team = context_name
                    # Ensure result_value is numeric before adding
                    try:
                        result_value = float(result_value)  # Or int() if you only have integers
                        team_results.setdefault(team, []).append(result_value)
                    except (ValueError, TypeError):
                        st.warning(f"Ungültiges Ergebnis für {shooter} im Team {team}: {result_value}.  Ergebnis wird ignoriert.")  # Inform user and skip
                        continue  # Skip this result if it's not a number


            sum_team_results = []
            for team, results in team_results.items():
                if results:  # Check if the team has any valid results
                    team_sum = sum(results)
                    sum_team_results.append({"Mannschaft": team, "Ergebnis": team_sum})
                else:
                   st.info(f"Keine Ergebnisse für das Team {team} gefunden. Das Team wird in der Wertung nicht berücksichtigt.")


            df_team = pd.DataFrame(sum_team_results)

            if not df_team.empty: # Check if the DataFrame is empty
                df_team = df_team.sort_values(by="Ergebnis", ascending=False)
                df_team.insert(0, "Platz", range(1, len(df_team) + 1))
                st.dataframe(df_team.set_index("Platz"))
            else:
                st.info("Keine gültigen Mannschaftsergebnisse zum Anzeigen.")
else:
    st.warning("Bitte erst Ergebnisse und Teilnehmerdaten eingeben.")  # More informative message