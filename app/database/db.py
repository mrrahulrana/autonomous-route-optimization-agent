import os
from typing import Optional


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/route_optimization",
)


class Database:
    """
    Database abstraction for persistent route history,
    agent context and optimization results.

    PostgreSQL integration will be implemented in a later commit.
    """

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or DATABASE_URL

    def health_check(self) -> bool:
        """
        Placeholder health check.

        Actual PostgreSQL connectivity will be added later.
        """
        return True


db = Database()