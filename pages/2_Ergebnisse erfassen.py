import streamlit as st
import json
from utils import load_competitions, load_participants, save_participants

st.title("Ergebnisse eingeben")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "shooters" in participants:
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))

    # Team-basierte Eingabe ODER separate Eingabe
    input_mode = st.radio("Eingabemodus", options=["Mannschaft", "Einzelperson"])

    if input_mode == "Mannschaft" and "teams" in participants:
        team_shooters = {}
        for team_name, team_members in participants["teams"].items():
            # Nur Schützen berücksichtigen, die auch in der Schützenliste vorhanden sind
            team_shooters[team_name] = [
                shooter for shooter in team_members if shooter in participants["shooters"]
            ]

        selected_team = st.selectbox("Mannschaft auswählen", options=list(team_shooters.keys()))

        # Überprüfen, ob Schützen für das ausgewählte Team vorhanden sind
        if team_shooters[selected_team]:
            selected_shooter = st.selectbox(
                "Schützen auswählen", options=team_shooters[selected_team]
            )
        else:
            st.warning(f"Keine Schützen für das Team '{selected_team}' gefunden.")
            selected_shooter = None  # Oder eine andere geeignete Behandlung

    else:  # Einzelperson
        selected_shooter = st.selectbox("Schützen auswählen", options=list(participants["shooters"].keys()))

    if selected_shooter: # Nur wenn ein Schütze ausgewählt wurde
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

        # Sortierung nach Team (falls vorhanden) und dann Ergebnis
        sorted_shooters = []
        if "teams" in participants:
            for team_name in sorted(participants["teams"].keys()):
                team_members = [shooter for shooter in participants["teams"][team_name] if shooter in results_table or shooter in participants["shooters"]] # Alle Schützen des Teams anzeigen
                sorted_team_members = sorted(team_members, key=lambda x: results_table.get(x, -1), reverse=True) # Sortierung auch für Schützen ohne Ergebnis
                sorted_shooters.extend(sorted_team_members)

        # Hinzufügen von Schützen ohne Team (und ohne Ergebnis) am Ende
        shooters_without_team = [shooter for shooter in participants["shooters"] if shooter not in sorted_shooters]
        sorted_shooters.extend(shooters_without_team)

        for shooter in sorted_shooters:
            result = results_table.get(shooter, "") # Leeres Ergebnis für neue Schützen
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

else:
    st.warning("Bitte erst Wettbewerbe und Schützen anlegen.")