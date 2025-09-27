# schema_discovery.py
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.engine import Engine
from rapidfuzz import process, fuzz

class SchemaDiscovery:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine: Engine = create_engine(connection_string, future=True)
        self.metadata = MetaData()

    def analyze_database(self) -> dict:
        inspector = inspect(self.engine)
        tables = {}
        for table_name in inspector.get_table_names():
            cols = inspector.get_columns(table_name)
            pk = inspector.get_pk_constraint(table_name)
            fks = inspector.get_foreign_keys(table_name)
            sample = []
            try:
                with self.engine.connect() as conn:
                    res = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))
                    sample = [dict(row._mapping) for row in res.fetchall()]
            except Exception:
                sample = []
            tables[table_name] = {
                "columns": [{ "name": c["name"], "type": str(c["type"]) } for c in cols],
                "primary_key": pk.get("constrained_columns"),
                "foreign_keys": fks,
                "sample": sample
            }
        return {"tables": tables}

    def map_nl_to_column(self, query_term: str, schema: dict, top_n=3):
        """
        Fuzzy-match a natural-language term to table.column choices.
        Returns list of tuples (choice, score).
        """
        choices = []
        for tbl, meta in schema["tables"].items():
            for col in meta["columns"]:
                choices.append(f"{tbl}.{col['name']}")
        if not choices:
            return []
        best = process.extract(query_term, choices, scorer=fuzz.WRatio, limit=top_n)
        # best entries are tuples: (choice, score, idx)
        return [(entry[0], entry[1]) for entry in best]
