import streamlit as st
import json
from utils import load_competitions, load_participants, save_participants

st.title("Ergebnisse eingeben")

competitions = load_competitions()
participants = load_participants()

if competitions and participants and "teams" in participants and "shooters" in participants:
    selected_competition = st.selectbox("Wettbewerb auswählen", options=list(competitions.keys()))

    # Struktur zur Speicherung der Teilnahme-Kontexte:
    shooter_contexts = {}
    for shooter_name, shooter_data in participants["shooters"].items():
        shooter_contexts[shooter_name] = []
        if "teams" in shooter_data:
            for team_name in shooter_data["teams"]:
                shooter_contexts[shooter_name].append({"type": "team", "name": team_name})
        shooter_contexts[shooter_name].append({"type": "individual"})  # Immer auch einzeln

    all_shooters_with_context = []
    for shooter, contexts in shooter_contexts.items():
        for context in contexts:
            all_shooters_with_context.append({"shooter": shooter, "context_type": context["type"], "context_name": context.get("name", None)})

    selected_shooter_context = st.selectbox("Schützen auswählen (mit Kontext)", options=all_shooters_with_context,
                                             format_func=lambda x: f"{x['shooter']} ({x['context_type']}" + (f" - {x['context_name']})" if x.get('context_name') else ")"))


    if selected_shooter_context:
        result = st.number_input("Ergebnis eingeben")

        if st.button("Ergebnis speichern"):
            if selected_competition:
                if "results" not in participants:
                    participants["results"] = {}
                if selected_competition not in participants["results"]:
                    participants["results"][selected_competition] = {}

                shooter = selected_shooter_context["shooter"]
                context_type = selected_shooter_context["context_type"]
                context_name = selected_shooter_context.get("context_name")

                result_key = f"{shooter}-{context_type}" + (f"-{context_name}" if context_name else "") # Eindeutiger Schlüssel

                participants["results"][selected_competition][result_key] = result
                save_participants(participants)
                message_suffix = f" - {context_name}" if context_name else ""  # Korrekte Formatierung des Erfolgsmeldung
                st.success(f"Ergebnis für '{shooter}' ({context_type}{message_suffix}) im Wettbewerb '{selected_competition}' gespeichert.")
                st.rerun()
            else:
                st.error("Bitte Wettbewerb auswählen.")

        # Ergebnistabelle anzeigen (mit Kontext)
        st.subheader("Ergebnisse")
        if "results" in participants and selected_competition in participants["results"]:
            results_table = participants["results"][selected_competition]

            sorted_results = sorted(results_table.items(), key=lambda item: item[1], reverse=True) # Sortieren nach Ergebnis

            for result_key, result_value in sorted_results:
                parts = result_key.split("-")
                shooter = parts[0]
                context_type = parts[1] if len(parts) >= 2 else "Einzel" # Standardwert "Einzel", falls kein Kontexttyp
                context_name = "-".join(parts[2:]) if len(parts) > 2 else None

                team_name = context_name if context_type == "team" else "Einzel"

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(team_name)
                with col2:
                    st.write(shooter)
                with col3:
                    try:
                        result_value = int(result_value) if result_value != "" else 0
                    except ValueError:
                        result_value = 0
                    new_result = st.number_input("Ergebnis", value=result_value, key=f"{selected_competition}-{result_key}")
                with col4:
                    if st.button("Ändern", key=f"change-{selected_competition}-{result_key}"):
                        participants["results"][selected_competition][result_key] = new_result
                        save_participants(participants)
                        st.success("Ergebnis geändert.")
                        st.rerun()
        else:
            st.info("Noch keine Ergebnisse für diesen Wettbewerb.")

else:
    st.warning("Bitte erst Wettbewerbe und Schützen anlegen.")