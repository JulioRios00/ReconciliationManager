#Repositories
from repositories.repository import Repository
#Services
from common.custom_exception import CustomException
from common.error_messages import X_NOT_RECORDS
#Tables
from models.schema_nota_avulsa import *
#Libs
from sqlalchemy import and_, func, extract
from sqlalchemy.sql import text, alias, select
from sqlalchemy_pagination import paginate
import json
from flask import jsonify


class DadosItensRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, DadosItens)

class NotaEntradaRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, NotaEntrada)

class EmpresaRepository(Repository):
    def __init__(self, db_session):
        self.session = db_session
        super().__init__(db_session, EmpresaNotaAvulsa)

    def empresa(self, cnpj):
        return self.session.query(EmpresaNotaAvulsa).\
            filter(EmpresaNotaAvulsa.cpfcnpj.ilike(f'%{cnpj}%')).\
                first()