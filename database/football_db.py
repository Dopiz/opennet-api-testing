# ============================================================================
# EXAMPLE ONLY — NOT USED BY THE CURRENT TESTS.
# This illustrates how DB-consistency validation would plug into the framework
# (see "Validation Strategy" in the README). No live database is wired up.
# ============================================================================

from .psql_module import PsqlModule


class FootballDatabase:
    def __init__(self, client: PsqlModule) -> None:
        self._conn = client

    def get_countries(self):
        sql = "SELECT * FROM countries;"
        return self._conn.read_data(sql)

    def get_country(self, id: int):
        args = {
            "id": id,
        }
        sql = "SELECT * FROM countries WHERE id = %(id)s;"
        return self._conn.read_data(sql, args, fetchall=False)
