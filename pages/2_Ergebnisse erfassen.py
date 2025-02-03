import streamlit as st
import json
from utils import load_competitions, load_participants, save_participants

st.title("Ergebnisse eingeben")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "shooters" in participants and "teams" in participants:  # Check for teams
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))

    # Team-basierte Eingabe
    team_shooters = {}
    for team_name, team_members in participants["teams"].items():
        team_shooters[team_name] = [shooter for shooter in team_members if shooter in participants["shooters"]]

    selected_team = st.selectbox("Mannschaft auswählen", options=list(team_shooters.keys()))
    selected_shooter = st.selectbox("Schützen auswählen", options=team_shooters[selected_team]) # Filter shooters by team
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

    # Ergebnistabelle anzeigen (mit Team-Sortierung)
    st.subheader("Ergebnisse")
    if "results" in participants and selected_competition in participants["results"]:
        results_table = participants["results"][selected_competition]

        # Sortierung nach Team und dann Ergebnis
        sorted_shooters = []
        for team_name in sorted(team_shooters.keys()):  # Teams in alphabetischer Reihenfolge
            team_members = [shooter for shooter in team_shooters[team_name] if shooter in results_table]
            sorted_team_members = sorted(team_members, key=lambda x: results_table[x], reverse=True)
            sorted_shooters.extend(sorted_team_members)

        for shooter in sorted_shooters:
            result = results_table[shooter]
            team_name = next((team for team, members in participants["teams"].items() if shooter in members), "Kein Team") # Teamzuordnung
            col1, col2, col3, col4 = st.columns(4)  # Zusätzliche Spalte für Team
            with col1:
                st.write(team_name) # Team anzeigen
            with col2:
                st.write(shooter)
            with col3:
                new_result = st.number_input("Ergebnis", value=result, key=f"{selected_competition}-{shooter}")
            with col4:
                if st.button("Ändern", key=f"change-{selected_competition}-{shooter}"):
                    participants["results"][selected_competition][shooter] = new_result
                    save_participants(participants)
                    st.success("Ergebnis geändert.")
                    st.rerun()
    else:
        st.info("Noch keine Ergebnisse für diesen Wettbewerb.")

else:
    st.warning("Bitte erst Wettbewerbe, Schützen und Mannschaften anlegen.")