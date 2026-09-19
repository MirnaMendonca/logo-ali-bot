from database.database import Base, engine, ensure_schema
import database.models

Base.metadata.create_all(bind=engine)
ensure_schema()

print("Banco criado com sucesso!")