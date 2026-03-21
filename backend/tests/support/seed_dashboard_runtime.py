from __future__ import annotations

import sys
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine

from app.db.session import create_session_factory
from tests.support.dashboard_seed import reset_database, seed_dashboard_data


DATABASE_URL = "sqlite:///./legalboard.db"


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"clear", "seed"}:
        print("usage: seed_dashboard_runtime.py [clear|seed]")
        return 1

    action = sys.argv[1]
    reset_database(DATABASE_URL)

    if action == "clear":
        return 0

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    session_factory = create_session_factory(engine)
    session = session_factory()
    try:
        seed_dashboard_data(session, reference_date=date.today())
    finally:
        session.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
