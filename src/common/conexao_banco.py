#Services
from .secrets_manager import get_secret
#Libs
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import boto3
from contextlib import contextmanager
import os


client = boto3.client('secretsmanager', region_name='us-east-1')


def get_database_password():
    if os.getenv('ENVIRONMENT') != 'qa' and os.getenv('ENVIRONMENT') != 'prod':
        secret_name = 'arn:aws:secretsmanager:us-east-1:018061303185:secret:dev/elementarapp/postgresql-gCV4D2'
    else:
        secret_name = os.getenv('ELEMENTAR_SECRETS_MANAGER_ARN')
    return get_secret(secret_name)
    
 
SECRET_JSON = get_database_password()
engine = db.create_engine(f"postgresql://{SECRET_JSON['username']}:{SECRET_JSON['password']}@{SECRET_JSON['host']}/postgres")
connection = engine.connect()

# defining session
Session = sessionmaker(bind=engine)
# Do not use this object, you can have problems in postgresql. 
# Prefer to use the get_session function
session = Session()

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
