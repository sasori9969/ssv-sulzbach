import streamlit as st
import json
from utils import load_competitions, load_participants, save_participants

st.title("Ergebnisse eingeben")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "teams" in participants:
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))

    input_mode = st.radio("Eingabemodus", options=["Mannschaft", "Einzelperson"])

    if input_mode == "Mannschaft":
        team_shooters = {}
        for team_name, team_data in participants["teams"].items():
            team_members = team_data["members"]
            shooters_in_team = []
            for shooter_name, shooter_data in participants.get("shooters", {}).items():
                if "teams" in shooter_data and team_name in shooter_data["teams"]:
                    shooters_in_team.append(shooter_name)
            team_shooters[team_name] = shooters_in_team

        selected_team = st.selectbox("Mannschaft auswählen", options=list(team_shooters.keys()))

        if team_shooters.get(selected_team):
            selected_shooter = st.selectbox("Schützen auswählen", options=team_shooters[selected_team])
        else:
            st.warning(f"Das Team '{selected_team}' hat keine zugeordneten Schützen.")
            selected_shooter = None

    else:  # Einzelperson
        all_shooters = set(participants.get("shooters", {}).keys())
        for team_members in participants.get("teams", {}).values():
            all_shooters.update(team_members)
        selected_shooter = st.selectbox("Schützen auswählen", options=list(all_shooters))

    if selected_shooter:
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

        # Ergebnistabelle anzeigen (mit Team-Sortierung und Anzeige aller Schützen)
        st.subheader("Ergebnisse")
        if "results" in participants and selected_competition in participants["results"]:
            results_table = participants["results"][selected_competition]

            all_shooters_in_comp = set()
            if "teams" in participants:
                for team_name in sorted(participants["teams"].keys()):
                    team_members = participants["teams"][team_name]
                    all_shooters_in_comp.update(team_members)
            if "shooters" in participants:
                all_shooters_in_comp.update(participants["shooters"].keys())

            sorted_shooters = sorted(list(all_shooters_in_comp), key=lambda x: results_table.get(x, -1), reverse=True)

            for shooter in sorted_shooters:
                result = results_table.get(shooter, "")
                team_name = next((team for team, members in participants["teams"].items() if shooter in members), "Kein Team")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(team_name)
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

    elif input_mode == "Mannschaft" and selected_team and not team_shooters.get(selected_team):
        st.warning(f"Das Team '{selected_team}' hat keine zugeordneten Schützen.")

else:
    st.warning("Bitte erst Wettbewerbe und Schützen anlegen.")