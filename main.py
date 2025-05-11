import asyncio

import streamlit as st
import pandas as pd
import time
from streamlit_player import st_player


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

            if txt and txt not in ["0", "nan", "esercizio", "serie", "ripetizioni", "recupero", "note esercizio",
                                   "note extra", "video", "note progressione"]:
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

            if len(cell_val) < 5 and cell_val.strip() not in ["", "0", "nan"]:
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
    settimane = {}
    for key, exs in allenamenti.items():
        sett, g = key.split(' - ')
        settimane.setdefault(sett, {})[g] = exs

    # Selezione settimana e giorno
    settimana_sel = st.selectbox("Scegli la settimana", list(settimane.keys()))
    giorno_sel = st.selectbox("Scegli il giorno", list(settimane[settimana_sel].keys()))
    esercizi = settimane[settimana_sel][giorno_sel]

    # Inizializza completamenti
    allen_id = f"{settimana_sel}-{giorno_sel}"
    if allen_id not in st.session_state:
        st.session_state[allen_id] = set()

    # Barra di progresso
    completati = st.session_state[allen_id]
    total = len(esercizi)
    done = len(completati)
    st.progress(done / total)
    st.write(f"{done} di {total} esercizi completati")

    # Lista esercizi con bottone completamento
    for i, ex in enumerate(esercizi, start=1):
        ex_key = f"{allen_id}-{i}"
        if ex_key not in st.session_state:
            st.session_state[ex_key] = False
        try:
            rec = int(ex.get('Recupero') or 0)
        except Exception:
            rec = 0
        testo = f"{ex['Esercizio']}"
        if st.session_state[ex_key]: testo = f":green-background[{ex['Esercizio']}]"

        with st.expander(testo):
            st.write(f"**Serie:** {ex['Serie']}  •  **Ripetizioni:** {ex['Ripetizioni']}")

            # Gestione video con embed
            video_url = ex.get('Video') or ''
            if video_url:
                embed_url = (
                    video_url
                    .replace('youtube.com/shorts/', 'youtube.com/embed/')
                    .replace('youtu.be/', 'www.youtube.com/embed/')
                )
                st.video(embed_url)

            st.write(f"**Note:** {ex['Note']}")
            st.write(f"**Recupero:** {rec}s  •  **Note Extra:** {ex['Note Extra']}")
            st.write(f"**Progressione:** {ex['Progressione']}")

            if not st.session_state[ex_key]:
                if st.button("✅ Segna come completato", key=f"comp_{ex_key}"):
                    st.session_state[ex_key] = True
                    st.session_state[allen_id].add(i)
                    st.rerun()
            else:
                st.success("Esercizio completato")


            placeholder = st.empty()
            if st.button("▶️ Avvia Recupero", key=f"timer_{ex_key}"):
                for sec in range(rec, -1, -1):
                    placeholder.metric("Tempo rimanente", f"{sec}s")
                    time.sleep(1)
                placeholder.success("✅ Recupero completato!")

            # Input pesi e serie
            st.number_input("Peso (kg)", key=f"peso_{i}", step=0.5)
            st.number_input("Serie fatte", key=f"serie_{i}", min_value=0)
            st.write("---")
