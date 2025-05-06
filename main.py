import streamlit as st
import pandas as pd
import time

# Carica il file Excel
@st.cache_data
def load_excel():
    file_path = "Davide berti- aprile.xlsx"
    df = pd.read_excel(file_path, sheet_name="Programmi", header=None)
    return df

df = load_excel()

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

# Streamlit UI
st.title("📋 Programma Allenamento Personalizzato")
if not allenamenti:
    st.warning("Nessun allenamento valido trovato.")
else:
    sel = st.selectbox("Seleziona allenamento", list(allenamenti.keys()))
    st.subheader(sel)

    # Visualizza esercizi con timer di recupero inline
    for i, ex in enumerate(allenamenti[sel], start=1):
        try:
            rec = int(ex.get('Recupero', None) or 0)
        except Exception:
            rec = 60
        with st.expander(f"{i}. {ex['Esercizio']}"):
            st.write(f"Serie: {ex['Serie']} - Ripetizioni: {ex['Ripetizioni']}")
            if ex['Video']:
                st.markdown(f"[Video]({ex['Video']})")
            st.write(f"Note: {ex['Note']}")
            st.write(f"Recupero: {rec}s")
            st.write(f"Note Extra: {ex['Note Extra']}")
            st.write(f"Progressione: {ex['Progressione']}")

            # Usa un solo placeholder per tutti gli elementi del timer
            timer_placeholder = st.empty()
            # Avvia il countdown in modo bloccante, ma all'interno dello stesso placeholder
            if st.button("▶️ Avvia Recupero", key=f"timer_{i}"):
                for sec in range(rec, -1, -1):
                    # Aggiorna timer e barra di progresso
                    timer_placeholder.metric(label="Tempo rimanente", value=f"{sec}s")
                    time.sleep(1)
                timer_placeholder.success("✅ Recupero completato!")


            st.number_input("Peso (kg)", key=f"peso_{i}", step=0.5)
            st.number_input("Serie fatte", key=f"serie_{i}", min_value=0)
            st.write("---")
