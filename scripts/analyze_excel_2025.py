import sys
import os
import json
import re
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.config import settings


def normalize_name(name):
    if not name:
        return name
    name = str(name)
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", name.strip()).lower()


def names_match(name1, name2, threshold=0.6):
    if not name1 or not name2:
        return False
    words1 = set(normalize_name(name1).split())
    words2 = set(normalize_name(name2).split())
    if not words1 or not words2:
        return False
    intersection = words1 & words2
    min_words = min(len(words1), len(words2))
    if min_words == 0:
        return False
    return len(intersection) / min_words >= threshold


def find_user_by_fuzzy_name(users_by_name, target_name):
    if not target_name:
        return None
    target = normalize_name(target_name)
    for key, user in users_by_name.items():
        if names_match(key, target):
            return user
    return None


def analyze_excel(filepath: str, db_url: str = None):
    if db_url is None:
        db_url = settings.DATABASE_URL.replace("@db:", "@localhost:5433/")

    engine = create_engine(db_url)
    session = Session(engine)

    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()
    session.commit()

    users_by_email = {}
    users_by_name = {}
    all_users = session.query(User).all()
    for user in all_users:
        if user.email:
            users_by_email[user.email.strip().lower()] = user
        normalized = normalize_name(user.name)
        users_by_name[normalized] = user

    results = []
    by_email_count = 0
    by_name_count = 0
    not_found_count = 0
    inactive_count = 0
    total = len(df)

    for idx, row in df.iterrows():
        email = str(row.get("Correo Corporativo", "")).strip().lower() if pd.notna(row.get("Correo Corporativo")) else ""
        name = str(row.get("Responsable", "")).strip() if pd.notna(row.get("Responsable")) else ""
        indicator = str(row.get("Nombre del Indicador", "")).strip() if pd.notna(row.get("Nombre del Indicador")) else ""

        user = None
        match_type = None

        if email and email in users_by_email:
            user = users_by_email[email]
            match_type = "email"

        if not user and name:
            user = find_user_by_fuzzy_name(users_by_name, name)
            if user:
                match_type = "name_fuzzy"

        if user:
            if not user.is_active:
                status = "inactive"
                inactive_count += 1
            else:
                status = "active"

            if match_type == "email":
                by_email_count += 1
            else:
                by_name_count += 1
        else:
            status = "not_found"
            not_found_count += 1

        results.append({
            "fila": idx + 2,
            "responsable": name,
            "correo": email,
            "indicador": indicator,
            "estado": status,
            "match_type": match_type,
        })

    session.close()
    engine.dispose()

    report = {
        "archivo": filepath,
        "total_filas": total,
        "por_correo": by_email_count,
        "por_nombre": by_name_count,
        "no_encontrados": not_found_count,
        "inactivos": inactive_count,
        "detalle": results,
    }

    return report


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/analyze_excel_2025.py <ruta_excel> [database_url]")
        print("Ejemplo: python scripts/analyze_excel_2025.py indicadores_2025.xlsx")
        sys.exit(1)

    filepath = sys.argv[1]
    db_url = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(filepath):
        print(f"Error: archivo no encontrado: {filepath}")
        sys.exit(1)

    report = analyze_excel(filepath, db_url)

    output_path = f"analisis_{Path(filepath).stem}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Total filas: {report['total_filas']}")
    print(f"  ✓ Por correo: {report['por_correo']}")
    print(f"  ✓ Por nombre (fuzzy): {report['por_nombre']}")
    print(f"  ✗ No encontrados: {report['no_encontrados']}")
    print(f"  ⚠ Inactivos: {report['inactivos']}")
    print(f"\nReporte detallado: {output_path}")


if __name__ == "__main__":
    main()
