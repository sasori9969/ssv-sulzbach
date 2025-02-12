import streamlit as st
import json

# Dummy-Funktionen zum Laden und Speichern (ersetze diese durch deine tatsächlichen Funktionen)
def load_participants():
    try:
        with open("participants.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_participants(participants):
    with open("participants.json", "w") as f:
        json.dump(participants, f, indent=4)

st.title("Mannschaften und Schützen verwalten")

participants = load_participants()

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

# Eingabe für Schützen
st.subheader("Schützen hinzufügen/bearbeiten")
shooter_name = st.text_input("Name")
shooter_firstname = st.text_input("Vorname")

if st.button("Schützen hinzufügen"):
    if shooter_name and shooter_firstname:
        full_name = f"{shooter_name}, {shooter_firstname}"
        if full_name not in participants.get("shooters", {}):
            participants.setdefault("shooters", {})
            participants["shooters"][full_name] = {"teams": []}
            save_participants(participants)
            st.success(f"Schütze '{full_name}' hinzugefügt.")
            st.rerun()
        else:
            st.error(f"Schütze '{full_name}' existiert bereits.")
    else:
        st.error("Bitte Name und Vorname eingeben.")

# Eingabe für Mannschaften
st.subheader("Mannschaften hinzufügen/bearbeiten")
team_name = st.text_input("Mannschaftsname")

if st.button("Mannschaft hinzufügen"):
    if team_name:
        if team_name not in participants.get("teams", {}):
            participants.setdefault("teams", {})
            participants["teams"][team_name] = {"members": []}
            save_participants(participants)
            st.success(f"Mannschaft '{team_name}' hinzugefügt.")
            st.rerun()
        else:
            st.error(f"Mannschaft '{team_name}' existiert bereits.")
    else:
        st.error("Bitte Mannschaftsnamen eingeben.")

# Anzeige und Bearbeitung von Schützen und Mannschaften
st.subheader("Vorhandene Schützen")
if "shooters" in participants:
    for shooter_name, shooter_data in participants["shooters"].items():
        st.write(f"- {shooter_name} (Teams: {', '.join(shooter_data['teams'])})")

        if st.checkbox(f"Bearbeiten: {shooter_name}"):
            new_name = st.text_input("Neuer Name", value=shooter_name.split(",")[0].strip())
            new_firstname = st.text_input("Neuer Vorname", value=shooter_name.split(",")[1].strip())

            if st.button("Änderungen speichern", key=f"save_shooter_{shooter_name}"):
                if new_name and new_firstname:
                    del participants["shooters"][shooter_name]
                    participants["shooters"][f"{new_name}, {new_firstname}"] = shooter_data
                    save_participants(participants)
                    st.success(f"Schütze '{shooter_name}' bearbeitet.")
                    st.rerun()
                else:
                    st.error("Bitte Name und Vorname eingeben.")

            if st.button("Schütze löschen", key=f"delete_shooter_{shooter_name}"):
                del participants["shooters"][shooter_name]
                save_participants(participants)
                st.success(f"Schütze '{shooter_name}' gelöscht.")
                st.rerun()

st.subheader("Vorhandene Mannschaften")
if "teams" in participants:
    for team_name, team_data in participants["teams"].items():
        st.write(f"- {team_name} (Mitglieder: {', '.join(team_data['members'])})")

        if st.checkbox(f"Bearbeiten: {team_name}"):
            new_team_name = st.text_input("Neuer Mannschaftsname", value=team_name)

            if st.button("Änderungen speichern", key=f"save_team_{team_name}"):
                if new_team_name and new_team_name not in participants.get("teams", {}): # Duplikatprüfung vor Änderung
                    del participants["teams"][team_name]
                    participants["teams"][new_team_name] = team_data
                    save_participants(participants)
                    st.success(f"Mannschaft '{team_name}' bearbeitet.")
                    st.rerun()
                elif new_team_name in participants.get("teams", {}):
                    st.error(f"Mannschaft '{new_team_name}' existiert bereits.")
                else:
                    st.error("Bitte Mannschaftsnamen eingeben.")

            if st.button("Mannschaft löschen", key=f"delete_team_{team_name}"):
                del participants["teams"][team_name]
                # Entferne die Mannschaft aus den Schützen
                for shooter in participants.get("shooters", {}): # Sicherstellen, dass 'shooters' existiert
                    if team_name in participants["shooters"][shooter]["teams"]:
                        participants["shooters"][shooter]["teams"].remove(team_name)

                save_participants(participants)
                st.success(f"Mannschaft '{team_name}' gelöscht.")
                st.rerun()

st.subheader("Mitglieder zu Mannschaften hinzufügen")
if "teams" in participants and "shooters" in participants:
    selected_team = st.selectbox("Mannschaft auswählen", options=list(participants["teams"].keys()))
    available_shooters = list(participants["shooters"].keys())
    selected_members = st.multiselect("Mitglieder auswählen", options=available_shooters)

    if st.button("Mitglieder hinzufügen"):
        if selected_team and selected_members:
            participants["teams"][selected_team]["members"] = selected_members
            # Aktualisiere auch die Team-Zugehörigkeit der Schützen
            for member in selected_members:
                if selected_team not in participants["shooters"][member]["teams"]:
                    participants["shooters"][member]["teams"].append(selected_team)
            save_participants(participants)
            st.success(f"Mitglieder zu '{selected_team}' hinzugefügt.")
            st.rerun()
        else:
            st.error("Bitte Mannschaft und Mitglieder auswählen.")