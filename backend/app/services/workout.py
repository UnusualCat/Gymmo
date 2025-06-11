from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.models import Program, Workout
from backend.app.services.google_drive import drive_service

def is_valid_exercise(ex: Dict) -> bool:
    for k, v in ex.items():
        if v is not None and pd.notna(v):
            txt = str(v).strip().lower()
            if txt and txt not in ["0", "nan", "esercizio", "serie", "ripetizioni", "recupero", 
                                 "note esercizio", "note extra", "video", "note progressione"]:
                return True
    return False

def extract_workouts(df: pd.DataFrame) -> Dict[str, List[Dict]]:
    allenamenti = {}
    header_row_idx = None

    # Find header row
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
                empty_rows = 0
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

                if is_valid_exercise(esercizio) and cell_val != "":
                    empty_rows = 0
                    allenamenti[current_label].append(esercizio)
                else:
                    empty_rows += 1

                if empty_rows >= 2:
                    if allenamenti[current_label]:
                        giorno += 1
                        current_label = f"Settimana {settimana} - Giorno {giorno}"
                        allenamenti[current_label] = []
                    empty_rows = 0

        if not allenamenti[current_label]:
            del allenamenti[current_label]

        settimana += 1

    return allenamenti

def process_program(db: Session, program: Program) -> None:
    """Process a program's Excel file and store workouts in the database."""
    df = drive_service.download_file(program.google_drive_file_id)
    if df is None:
        return

    workouts = extract_workouts(df)
    
    # Clear existing workouts
    db.query(Workout).filter(Workout.program_id == program.id).delete()
    
    # Add new workouts
    for label, exercises in workouts.items():
        week, day = label.split(" - ")
        week_num = int(week.split()[-1])
        day_num = int(day.split()[-1])
        
        for exercise in exercises:
            workout = Workout(
                program_id=program.id,
                week_number=week_num,
                day_number=day_num,
                exercise_name=exercise["Esercizio"],
                series=exercise["Serie"],
                repetitions=exercise["Ripetizioni"],
                rest_time=exercise["Recupero"],
                notes=exercise["Note"],
                extra_notes=exercise["Note Extra"],
                progression=exercise["Progressione"],
                video_url=exercise["Video"]
            )
            db.add(workout)
    
    db.commit() 