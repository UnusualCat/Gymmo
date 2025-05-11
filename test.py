import pandas as pd

df = pd.read_excel("Davide berti- aprile.xlsx", sheet_name="Programmi", header=None)

def is_valid_exercise(ex):
    for k, v in ex.items():
        if v is not None and pd.notna(v):
            txt = str(v).strip().lower()

            if txt and txt not in ["0", "nan", "esercizio", "serie", "ripetizioni", "recupero", "note esercizio", "note extra", "video", "note progressione"]:
                return True
    return False


def extract_workouts(df):
    allenamenti = {}
    header_row_idx = None

    # Trova la riga con le intestazioni (dove c'è almeno una cella "Esercizio")
    for i, row in df.iterrows():
        row_str = [str(cell).strip().lower() if pd.notna(cell) else "" for cell in row]
        if "esercizio" in row_str:
            header_row_idx = i
            break

    if header_row_idx is None:
        return {}

    header_row = df.iloc[header_row_idx]
    esercizio_cols = [i for i, val in enumerate(header_row) if str(val).strip().lower() == "esercizio"]

    settimana = 1

    for col_idx in esercizio_cols:
        giorno = 1
        current_label = f"Settimana {settimana} - Giorno {giorno}"
        allenamenti[current_label] = []

        empty_rows = 0

        for i in range(header_row_idx + 1, len(df)):
            cell = df.iat[i, col_idx]
            cell_val = str(cell).strip() if pd.notna(cell) else ""

            if len(cell_val)<5 and cell_val.strip() not in ["", "0", "nan"]:
                empty_rows += 1
            else:
                empty_rows = 0  # reset
                esercizio = {
                    "Esercizio": cell_val,
                    "Video": df.iat[i, col_idx + 1] if col_idx + 1 < len(df.columns) else "",
                    "Note": df.iat[i, col_idx + 2] if col_idx + 2 < len(df.columns) else "",
                    "Serie": df.iat[i, col_idx + 3] if col_idx + 3 < len(df.columns) else "",
                    "Ripetizioni": df.iat[i, col_idx + 4] if col_idx + 4 < len(df.columns) else "",
                    "Recupero": df.iat[i, col_idx + 8] if col_idx + 8 < len(df.columns) else "",
                    "Note Extra": df.iat[i, col_idx + 7] if col_idx + 7 < len(df.columns) else "",
                    "Progressione": df.iat[i, col_idx + 13] if col_idx + 13 < len(df.columns) else "",
                }

                # Validazione
                if is_valid_exercise(esercizio) and cell_val != "":
                    empty_rows = 0
                    allenamenti[current_label].append(esercizio)
                else:
                    empty_rows += 1

                # Due righe consecutive non valide -> nuovo giorno
                if empty_rows >= 2:
                    if allenamenti[current_label]:
                        giorno += 1
                        current_label = f"Settimana {settimana} - Giorno {giorno}"
                        allenamenti[current_label] = []
                    empty_rows = 0

            # Due righe vuote = nuovo giorno
            if empty_rows >= 2:
                if allenamenti[current_label]:  # Se ha raccolto qualcosa
                    giorno += 1
                    current_label = f"Settimana {settimana} - Giorno {giorno}"
                    allenamenti[current_label] = []
                empty_rows = 0  # reset

        # Se il blocco è completamente vuoto lo rimuovo
        if not allenamenti[current_label]:
            del allenamenti[current_label]

        settimana += 1

    return allenamenti

allenamenti = extract_workouts(df)
if "timer_started" not in st.session_state:
    st.session_state.timer_started = False
    st.session_state.start_time = 0

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Avvia Timer Recupero"):
        st.session_state.timer_started = True
        st.session_state.start_time = time.time()
with col2:
    if st.button("⏹️ Ferma Timer"):
        st.session_state.timer_started = False

if st.session_state.timer_started:
    elapsed = int(time.time() - st.session_state.start_time)
    st.info(f"⏱ Tempo trascorso: {elapsed} secondi")
for k, v in allenamenti.items():
    print(k,v)
