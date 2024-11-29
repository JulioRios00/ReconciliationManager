#Repositories
from repositories.repository import Repository
#Tables
from models.schema_ccs import Fligth

class FligthRepository(Repository):
    def __init__(self, db_session):
        super().__init__(db_session, Fligth)       
        
    