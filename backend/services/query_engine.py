# query_engine.py
import time
from typing import Dict, Any
from sqlalchemy import create_engine, text
from .schema_discovery import SchemaDiscovery
from .document_processor import DocumentProcessor
import re
from functools import lru_cache

class SimpleCache:
    def __init__(self):
        self.store = {}

    def set(self, key, value, ttl=300):
        self.store[key] = (value, time.time()+ttl)

    def get(self, key):
        entry = self.store.get(key)
        if not entry:
            return None
        val, exp = entry
        if time.time() > exp:
            del self.store[key]
            return None
        return val

class QueryEngine:
    def __init__(self, connection_string: str):
        self.conn_str = connection_string
        self.engine = create_engine(connection_string, future=True)
        self.schema = SchemaDiscovery(connection_string).analyze_database()
        self.doc_processor = DocumentProcessor()
        self.cache = SimpleCache()
        self.history = []

    def classify(self, user_query: str) -> str:
        q = user_query.lower()
        # heuristics
        if any(k in q for k in ["resume", "cv", "document", "review", "mentions", "mention", "resumes"]):
            return "document"
        if any(k in q for k in ["count", "average", "sum", "how many", "list", "who", "which", "top", "hired", "salary", "employees", "department", "dept", "turnover"]):
            return "sql"
        return "hybrid"

    def safe_sql_from_nl(self, user_query: str):
        """
        Very simple and safe NL->SQL mapping for demo queries.
        This intentionally avoids executing arbitrary generated SQL.
        Handles common patterns requested in assignment.
        """
        q = user_query.lower()

        # How many employees
        if "how many" in q and "employee" in q:
            return "SELECT COUNT(*) as count FROM employees"

        # Average salary by department
        if "average salary" in q or "avg salary" in q:
            return "SELECT dept_id, AVG(annual_salary) as avg_salary FROM employees GROUP BY dept_id"

        # List employees hired this year
        if "hired this year" in q or "hired in" in q:
            from datetime import date
            year = date.today().year
            return f"SELECT * FROM employees WHERE substr(join_date,1,4) = '{year}' LIMIT 500"

        # Top N highest paid
        m_top = re.search(r"top\s+(\d+)", q)
        if m_top and "highest" in q and "paid" in q:
            n = int(m_top.group(1))
            return f"SELECT dept_id, full_name, annual_salary FROM employees ORDER BY annual_salary DESC LIMIT {max(1,min(n,100))}"

        # Simple list / show me / filter by skill/department
        if q.startswith("list ") or "show me" in q or q.startswith("show "):
            # try skill match
            m = re.search(r"(python|java|sql|ml|management|hr|product|engineering|leadership)", q)
            if m:
                skill = m.group(1)
                return f"SELECT * FROM employees WHERE lower(skills) LIKE '%{skill}%' LIMIT 500"
            # department by name
            m2 = re.search(r"department (\w+)|dept(?:artment)? (\w+)|in (\w+ department|\w+ dept|\w+)", q)
            # fallback to returning all employees
            return "SELECT * FROM employees LIMIT 500"

        # Average salary overall
        if "average salary overall" in q or q == "average salary":
            return "SELECT AVG(annual_salary) as avg_salary FROM employees"

        # Default: None -> indicates cannot map
        return None

    def process_query(self, user_query: str) -> Dict[str, Any]:
        start = time.time()
        cached = self.cache.get(user_query)
        if cached:
            return {"from_cache": True, "time": 0.0, "result": cached, "query_type": "cached"}
        qtype = self.classify(user_query)
        results = {"sql": None, "docs": None}
        # SQL part
        if qtype in ("sql", "hybrid"):
            sql = self.safe_sql_from_nl(user_query)
            if sql:
                try:
                    with self.engine.connect() as conn:
                        res = conn.execute(text(sql))
                        # fetch rows safely
                        rows = [dict(r._mapping) for r in res.fetchall()]
                        results["sql"] = rows
                except Exception as e:
                    results["sql"] = {"error": str(e)}
            else:
                results["sql"] = {"error": "Could not parse to SQL automatically."}
        # Document part
        if qtype in ("document", "hybrid"):
            docs = self.doc_processor.query(user_query, top_k=5)
            results["docs"] = docs

        elapsed = time.time() - start
        # cache results
        self.cache.set(user_query, results, ttl=300)
        self.history.insert(0, {"query": user_query, "type": qtype, "time": elapsed})
        return {"from_cache": False, "time": round(elapsed, 4), "result": results, "query_type": qtype}
