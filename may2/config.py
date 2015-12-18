import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('postgres://ihbjxysaapeyno:ic8wo1hLKwlP37nA4DX0YhTAUD@ec2-107-21-223-110.compute-1.amazonaws.com:5432/d5jsisalsn4a2d')
Session = sessionmaker(bind=engine)


