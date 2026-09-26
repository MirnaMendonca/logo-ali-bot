from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///database/logoali.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def ensure_schema():
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    order_columns = {
        column["name"] for column in inspector.get_columns("orders")
    }

    with engine.begin() as connection:
        if "opening_name" not in order_columns:
            connection.execute(
                text("ALTER TABLE orders ADD COLUMN opening_name VARCHAR")
            )

        if "return_name" not in order_columns:
            connection.execute(
                text("ALTER TABLE orders ADD COLUMN return_name VARCHAR")
            )

        if "dispatcher_name" in order_columns:
            connection.execute(
                text(
                    "UPDATE orders SET opening_name = dispatcher_name "
                    "WHERE opening_name IS NULL AND dispatcher_name IS NOT NULL"
                )
            )

        if "pf_exclusions_pj" not in order_columns:
            connection.execute(
                text("ALTER TABLE orders ADD COLUMN pf_exclusions_pj INTEGER NOT NULL DEFAULT 0")
            )
