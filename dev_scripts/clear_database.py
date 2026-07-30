from database.database import SessionLocal
from database.models import User, Order

session = SessionLocal()

try:
    session.query(Order).delete()
    session.query(User).delete()

    session.commit()

    print("✅ Banco limpo com sucesso!")

finally:
    session.close()
