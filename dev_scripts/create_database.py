from database.database import Base, engine
import database.models

Base.metadata.create_all(bind=engine)

print("Banco criado com sucesso!")