# Repositories
# Services
import jwt
from flask import g, request

# Libs
from sqlalchemy import and_

from common.conexao_banco import session
from common.custom_exception import CustomException
from common.error_messages import (
    USER,
    USER_BELONGS_TO_DEACTIVATED_CUSTOMER,
    X_NOT_FOUND,
)

# Tables
from models.schema_public import User


def get_current_user():
    jwt_encoded = request.headers["Authorization"]
    jwt_encoded = jwt_encoded.replace("Bearer ", "")
    jwt_decoded = jwt.decode(jwt_encoded, options={"verify_signature": False})
    username = ""
    if "cognito:username" in jwt_decoded:
        username = jwt_decoded["cognito:username"]
    elif "username" in jwt_decoded:
        username = jwt_decoded["username"]

    user = (
        session.query(User)
        .filter(
            and_(
                User.Ativo.is_(True),
                User.Excluido.is_(False),
                User.Username == username,
            )
        )
        .first()
    )

    if not user:
        raise CustomException(X_NOT_FOUND.format(USER + ": " + username))
    if not user.Cliente.Ativo or user.Cliente.Excluido:
        raise CustomException(USER_BELONGS_TO_DEACTIVATED_CUSTOMER)

    g.user = user
    return user


def authenticate(app):
    print(app)
