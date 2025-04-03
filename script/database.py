from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import variables
import model

# Set up the engine
engine = create_engine(variables.DATABASE_URL)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session instance
session = Session()

model.Base.metadata.create_all(bind=engine)