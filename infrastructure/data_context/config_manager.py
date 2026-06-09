import sqlite3

class ConfigManager():
    def __init__(self):
        pass
    
    def get_repository_url() -> str | None:
        conn = sqlite3.connect("solvedesk.db")

        cursor = conn.cursor()

        cursor.execute("""
            SELECT repository_url
            FROM project_config
            ORDER BY id DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        conn.close()

        return result[0] if result else None