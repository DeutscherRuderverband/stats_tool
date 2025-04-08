import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import variables
import model

# Set up the engine
try:
    engine = create_engine(variables.DATABASE_URL)
except Exception as e:
    print(f"Fehler bei der Erstellung der Datenbank-engine, kontolliere die Datenbank-URL: {e}", file=sys.stderr)
    sys.exit(1)  # Exit with a non-zero status to indicate failure

# Set up session and create tables
try:
    Session = sessionmaker(bind=engine)
    session = Session()
    model.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Fehler beim Erstellen der Session oder der Tabellen: {e}", file=sys.stderr)
    sys.exit(1)