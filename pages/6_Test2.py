import streamlit as st
import pandas as pd
import os

# Datenablage (CSV-Dateien)
DATA_DIR = "schuetzenverein_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

PARTICIPANTS_FILE = os.path.join(DATA_DIR, "participants.csv")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.csv")
RESULTS_FILE = os.path.join(DATA_DIR, "results.csv")

def load_data():
    try:
        participants = pd.read_csv(PARTICIPANTS_FILE)
    except FileNotFoundError:
        participants = pd.DataFrame(columns=["First Name", "Last Name"])
    try:
        teams = pd.read_csv(TEAMS_FILE)
    except FileNotFoundError:
        teams = pd.DataFrame(columns=["Team Name"])
    try:
        results = pd.read_csv(RESULTS_FILE)
    except FileNotFoundError:
        results = pd.DataFrame(columns=["First Name", "Last Name", "Team Name", "Result"])
    return participants, teams, results

def save_data(participants, teams, results):
    participants.to_csv(PARTICIPANTS_FILE, index=False)
    teams.to_csv(TEAMS_FILE, index=False)
    results.to_csv(RESULTS_FILE, index=False)

participants, teams, results = load_data()

st.title("Schützenverein 1904 e.V. Sulzbach Competition Data")

# --- Teilnehmerverwaltung ---
st.subheader("Teilnehmer")
col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("Vorname")
with col2:
    last_name = st.text_input("Nachname")

# Auswahlfeld für den zu ändernden Teilnehmer
edit_participant_index = st.selectbox("Teilnehmer zum Ändern/Löschen", participants.index, format_func=lambda i: f"{participants['First Name'][i]} {participants['Last Name'][i]}", index=None)

if st.button("Hinzufügen/Ändern"):
    if first_name and last_name:
        new_participant = pd.DataFrame({"First Name": [first_name], "Last Name": [last_name]})
        if edit_participant_index is not None:  # Ändern
            participants.loc[edit_participant_index, 'First Name'] = first_name
            participants.loc[edit_participant_index, 'Last Name'] = last_name
            st.success(f"Teilnehmerdaten geändert.")
        else:  # Hinzufügen
            participants = pd.concat([participants, new_participant], ignore_index=True)
            st.success(f"Teilnehmer {first_name} {last_name} hinzugefügt.")
        save_data(participants, teams, results)
        st.experimental_rerun()  # Aktualisiert die Selectbox sofort

if st.button("Teilnehmer löschen"):
    if edit_participant_index is not None:
        participants = participants.drop(edit_participant_index).reset_index(drop=True)
        save_data(participants, teams, results)
        st.success("Teilnehmer gelöscht.")
        st.experimental_rerun()

if not participants.empty:
    st.dataframe(participants)

# --- Teamverwaltung ---
st.subheader("Teams")
team_name = st.text_input("Teamname")

# Auswahlfeld für bestehende Teams zum Bearbeiten
edit_team_index = st.selectbox("Team zum Bearbeiten/Ergänzen", teams.index, format_func=lambda i: teams['Team Name'][i], index=None)

available_participants = participants[["First Name", "Last Name"]].apply(lambda x: f"{x['First Name']} {x['Last Name']}", axis=1).tolist()
selected_members = st.multiselect("Teammitglieder auswählen/hinzufügen", available_participants)

if st.button("Team hinzufügen/bearbeiten"):
    if team_name and selected_members:
        if edit_team_index is not None:  # Bearbeiten/Ergänzen
            current_members = team_members[team_members['Team Name'] == teams['Team Name'][edit_team_index]]
            for member in selected_members:
                first, last = member.split(" ")
                if not ((current_members['First Name'] == first) & (current_members['Last Name'] == last)).any(): #Check if member is already in the team
                    new_team_member = pd.DataFrame({"Team Name": [teams['Team Name'][edit_team_index]], "First Name": [first], "Last Name": [last]})
                    team_members = pd.concat([team_members, new_team_member], ignore_index=True)
                    new_result = pd.DataFrame({"First Name": [first], "Last Name": [last], "Team Name": [teams['Team Name'][edit_team_index]], "Result": 0}, index=[0])
                    results = pd.concat([results, new_result], ignore_index=True)

            st.success(f"Team {teams['Team Name'][edit_team_index]} bearbeitet/ergänzt.")
        else:  # Hinzufügen
            new_team = pd.DataFrame({"Team Name": [team_name]})
            teams = pd.concat([teams, new_team], ignore_index=True)
            for member in selected_members:
                first, last = member.split(" ")
                new_team_member = pd.DataFrame({"Team Name": [team_name], "First Name": [first], "Last Name": [last]})
                team_members = pd.concat([team_members, new_team_member], ignore_index=True)
                new_result = pd.DataFrame({"First Name": [first], "Last Name": [last], "Team Name": [team_name], "Result": 0}, index=[0])
                results = pd.concat([results, new_result], ignore_index=True)
            st.success(f"Team {team_name} hinzugefügt mit Mitgliedern: {', '.join(selected_members)}")
        save_data(participants, teams, results, team_members)
        st.experimental_rerun()

if st.button("Team löschen"):
    if edit_team_index is not None:
        team_to_delete = teams['Team Name'][edit_team_index]
        teams = teams.drop(edit_team_index).reset_index(drop=True)
        team_members = team_members[team_members['Team Name'] != team_to_delete]
        results = results[results['Team Name'] != team_to_delete]
        save_data(participants, teams, results, team_members)
        st.success("Team gelöscht.")
        st.experimental_rerun()


if not teams.empty:
    st.dataframe(teams)

# --- Result Input ---
st.subheader("Result Input")
available_participants_results = participants[["First Name", "Last Name"]].apply(lambda x: f"{x['First Name']} {x['Last Name']}", axis=1).tolist()
participant_result = st.selectbox("Select Participant", available_participants_results)
team_for_result = st.selectbox("Select Team (or Individual)", ["Individual"] + teams["Team Name"].tolist())
result_score = st.number_input("Enter Result", min_value=0, step=1)

if st.button("Add Result"):
    if participant_result and result_score is not None:
        first, last = participant_result.split(" ")
        if team_for_result == "Individual":
          team_for_result = None  # Store None if it's an individual result
        existing_result_index = results[(results["First Name"] == first) & (results["Last Name"] == last) & (results["Team Name"] == team_for_result)].index
        if not existing_result_index.empty:
            results.loc[existing_result_index, "Result"] = result_score  # Update existing result
            st.success(f"Result for {participant_result} in {team_for_result} updated to {result_score}")

        else:
            new_result = pd.DataFrame({"First Name": [first], "Last Name": [last], "Team Name": [team_for_result], "Result": [result_score]})
            results = pd.concat([results, new_result], ignore_index=True)
            st.success(f"Result {result_score} added for {participant_result} in {team_for_result}.")

        save_data(participants, teams, results)
    else:
        st.warning("Please select a participant, team (or Individual) and enter a result.")


# --- Data Processing and Display ---
st.subheader("Individual Rankings")
individual_scores = results.groupby(["First Name", "Last Name"])["Result"].max().reset_index()
st.dataframe(individual_scores.sort_values("Result", ascending=False))

st.subheader("Team Rankings")
team_scores = results.groupby("Team Name")["Result"].sum().reset_index()
st.dataframe(team_scores.sort_values("Result", ascending=False))

# --- Export to CSV ---
if st.button("Export Results to CSV"):
    individual_scores.to_csv("individual_rankings.csv", index=False)
    team_scores.to_csv("team_rankings.csv", index=False)
    st.success("Results exported to CSV files.")


# --- Data Management (Raw Data Display) ---
if st.checkbox("Show Raw Data"):
    st.subheader("Participants")
    st.dataframe(participants)
    st.subheader("Teams")
    st.dataframe(teams)
    st.subheader("Results")
    st.dataframe(results)