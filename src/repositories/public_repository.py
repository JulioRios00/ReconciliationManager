#Repositorie
from repositories.repository import Repository
#Tables
from models.schema_public import *
#Libs
from sqlalchemy import and_, desc
from sqlalchemy_pagination import paginate


class EmpresaRepository(Repository):

    def __init__(self, db_session):
        super().__init__(db_session, Empresa)


class CategoriaEmpresaRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, CategoriaEmpresa)

    def get_all_pagined_order_by(self, page, per_page):
        items = self.session.query(CategoriaEmpresa).\
            filter(and_(CategoriaEmpresa.Ativo == True, CategoriaEmpresa.Excluido == False)).\
                order_by(CategoriaEmpresa.Categoria)

        items_paginate = paginate(items, int(page), int(per_page))
        items_json_list = [i.serialize() for i in items_paginate.items]
        items_paginate.items = items_json_list
        return vars(items_paginate)


class TipiRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, Tipi)

class UserRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, User)