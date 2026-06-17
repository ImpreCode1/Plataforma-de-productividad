"""
app/modules/position_groups/service.py

Construye el arbol jerarquico de position_groups (Vicepresidencia -> Direccion)
con el conteo de personas por nodo, incluyendo el acumulado de sus hijos.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_position_groups_tree(db: Session) -> list[dict]:
    """
    Devuelve el arbol completo de position_groups.
    Cada nodo de Direccion incluye su conteo directo de personas (users.position_group_id).
    Cada nodo de Vicepresidencia incluye la suma de personas de todas sus direcciones hijas.
    """
    query = text("""
        WITH RECURSIVE tree AS (
            -- Nivel raiz: vicepresidencias
            SELECT
                pg.id,
                pg.name,
                pg.level,
                pg.parent_id,
                pg.is_validated,
                0 AS depth
            FROM position_groups pg
            WHERE pg.parent_id IS NULL

            UNION ALL

            -- Hijos recursivos (direcciones, y futuros niveles si se agregan)
            SELECT
                child.id,
                child.name,
                child.level,
                child.parent_id,
                child.is_validated,
                tree.depth + 1
            FROM position_groups child
            JOIN tree ON child.parent_id = tree.id
        ),
        person_counts AS (
            SELECT position_group_id, COUNT(*) AS total
            FROM users
            WHERE position_group_id IS NOT NULL
            GROUP BY position_group_id
        )
        SELECT
            t.id,
            t.name,
            t.level,
            t.parent_id,
            t.is_validated,
            t.depth,
            COALESCE(pc.total, 0) AS personas_directas
        FROM tree t
        LEFT JOIN person_counts pc ON pc.position_group_id = t.id
        ORDER BY t.depth, t.name;
    """)

    rows = db.execute(query).mappings().all()

    # Indexar por id para armar el arbol en memoria
    nodes_by_id = {}
    for row in rows:
        nodes_by_id[row["id"]] = {
            "id": str(row["id"]),
            "name": row["name"],
            "level": row["level"],
            "is_validated": row["is_validated"],
            "personas_directas": row["personas_directas"],
            "personas_total": row["personas_directas"],  # se acumula abajo
            "children": [],
        }

    roots = []
    for row in rows:
        node = nodes_by_id[row["id"]]
        parent_id = row["parent_id"]
        if parent_id is None:
            roots.append(node)
        else:
            parent_node = nodes_by_id.get(parent_id)
            if parent_node:
                parent_node["children"].append(node)

    # Acumular personas_total desde las hojas hacia la raiz
    def accumulate(node: dict) -> int:
        total = node["personas_directas"]
        for child in node["children"]:
            total += accumulate(child)
        node["personas_total"] = total
        return total

    for root in roots:
        accumulate(root)

    return roots
