# Services
import os
from contextlib import contextmanager

import boto3

# Libs
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from .secrets_manager import get_secret

client = boto3.client("secretsmanager", region_name="us-east-1")


def get_database_password():
    if os.getenv("ENVIRONMENT") not in ["qa", "prod"]:
        secret_name = (
            "arn:aws:secretsmanager:us-east-1:018061303185:"
            "secret:dev/elementarapp/postgresql-gCV4D2"
        )
    else:
        secret_name = os.getenv("ELEMENTAR_SECRETS_MANAGER_ARN")
    return get_secret(secret_name)


SECRET_JSON = get_database_password()
if SECRET_JSON is None:
    raise ValueError("Failed to retrieve database secret from AWS Secrets Manager")
engine = db.create_engine(
    "postgresql://{}:{}@{}/postgres".format(
        SECRET_JSON["username"], SECRET_JSON["password"], SECRET_JSON["host"]
    )
)
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
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
