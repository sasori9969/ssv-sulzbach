import streamlit as st
import pandas as pd
import os

# Data Storage (using CSV files)
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
        results = pd.DataFrame(columns=["First Name", "Last Name", "Team Name", "Result"])  # Added Team Name to Results
    return participants, teams, results

def save_data(participants, teams, results):
    participants.to_csv(PARTICIPANTS_FILE, index=False)
    teams.to_csv(TEAMS_FILE, index=False)
    results.to_csv(RESULTS_FILE, index=False)

participants, teams, results = load_data()

st.title("Schützenverein 1904 e.V. Sulzbach Competition Data")

# --- Participant Management ---
st.subheader("Participants")
col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("First Name")
with col2:
    last_name = st.text_input("Last Name")
if st.button("Add Participant"):
    if first_name and last_name:
        new_participant = pd.DataFrame({"First Name": [first_name], "Last Name": [last_name]})
        participants = pd.concat([participants, new_participant], ignore_index=True)
        save_data(participants, teams, results) # Save after each change
        st.success(f"Participant {first_name} {last_name} added.")
    else:
        st.warning("Please enter both first and last names.")

# Auswahlfeld für den zu ändernden Teilnehmer
edit_participant_index = st.selectbox("Teilnehmer zum Ändern", participants.index, format_func=lambda i: f"{participants['First Name'][i]} {participants['Last Name'][i]}")

if st.button("Ändern"):
    if edit_participant_index is not None:
        # Füllen Sie die Eingabefelder mit den aktuellen Daten vor
        st.session_state.edit_first_name = participants['First Name'][edit_participant_index]
        st.session_state.edit_last_name = participants['Last Name'][edit_participant_index]

        # Eingabefelder für die neuen Daten (verwenden Sie st.session_state, um die Werte zu speichern)
        new_first_name = st.text_input("Neuer Vorname", value=st.session_state.edit_first_name)
        new_last_name = st.text_input("Neuer Nachname", value=st.session_state.edit_last_name)

        if st.button("Speichern"):
            # Aktualisieren Sie den DataFrame
            participants.loc[edit_participant_index, 'First Name'] = new_first_name
            participants.loc[edit_participant_index, 'Last Name'] = new_last_name
            save_data(participants, teams, results)
            st.success("Teilnehmerdaten geändert.")

# --- Team Management ---
st.subheader("Teams")
team_name = st.text_input("Team Name")
available_participants = participants[["First Name", "Last Name"]].apply(lambda x: f"{x['First Name']} {x['Last Name']}", axis=1).tolist()
selected_members = st.multiselect("Select Team Members", available_participants)

if st.button("Add Team"):
    if team_name and selected_members:
        new_team = pd.DataFrame({"Team Name": [team_name]})
        teams = pd.concat([teams, new_team], ignore_index=True)
        for member in selected_members:
            first, last = member.split(" ")
            new_result = pd.DataFrame({"First Name": [first], "Last Name": [last], "Team Name": [team_name], "Result": 0}, index=[0]) # Initialize Result to 0
            results = pd.concat([results, new_result], ignore_index=True)
        save_data(participants, teams, results)
        st.success(f"Team {team_name} added with members: {', '.join(selected_members)}")
    else:
        st.warning("Please enter a team name and select members.")

# Display and Edit/Delete Teams (similar edit/delete logic as Participants)
if not teams.empty:
    st.dataframe(teams)
    # Edit/Delete Team logic (similar to participants section)


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