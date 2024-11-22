from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, ListAttribute


class CruzamentoStatusTable(Model):
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "CruzamentoStatusTable"
    Id = UnicodeAttribute(hash_key=True)
    Cnpj = UnicodeAttribute()
    Cruzamento = UnicodeAttribute()
    Data = UTCDateTimeAttribute(null=True)
    Key = UnicodeAttribute(null=True)
    Status = UnicodeAttribute()
    Errors = ListAttribute(null=True)

class ICMSStatusTable(Model):
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "ICMSStatusTable"
    Id = UnicodeAttribute(hash_key=True)
    IdSped = UnicodeAttribute()
    DataSped = UTCDateTimeAttribute()
    TipoOperacao = UnicodeAttribute()
    DataCriacao = UTCDateTimeAttribute()
    DataAtualizacao = UTCDateTimeAttribute(null=True)
    Status = UnicodeAttribute()
    User = UnicodeAttribute()
    Analisys_id = UnicodeAttribute()
    Company = UnicodeAttribute()
    Errors = ListAttribute(null=True)

class NCMStatusTable(Model):
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "NCMStatusTable"
    Id = UnicodeAttribute(hash_key=True)
    IdSped = UnicodeAttribute()
    DataSped = UTCDateTimeAttribute()
    TipoOperacao = UnicodeAttribute()
    DataCriacao = UTCDateTimeAttribute()
    DataAtualizacao = UTCDateTimeAttribute(null=True)
    Status = UnicodeAttribute()
    User = UnicodeAttribute()
    Analisys_id = UnicodeAttribute()
    Company = UnicodeAttribute()
    Errors = ListAttribute(null=True)

class  ValidaC500StatusTable(Model):
    """
    A DynamoDB table
    """
    class Meta:
        table_name = 'ValidaC500StatusTable'
    Id = UnicodeAttribute(hash_key=True)
    IdSPEDFiscal = UnicodeAttribute()
    IdSPEDContrib = UnicodeAttribute()
    DataSped = UTCDateTimeAttribute()
    DataCriacao = UTCDateTimeAttribute()
    DataAtualizacao = UTCDateTimeAttribute(null=True)
    Status = UnicodeAttribute()
    User = UnicodeAttribute()
    Analisys_id = UnicodeAttribute()
    Company = UnicodeAttribute()
    Errors = ListAttribute(null=True)

class ValidaD100StatusTable(Model):
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "ValidaD100StatusTable"
    Id = UnicodeAttribute(hash_key=True)
    IdSPEDFiscal = UnicodeAttribute()
    IdSPEDContrib = UnicodeAttribute()
    DataSped = UTCDateTimeAttribute()
    DataCriacao = UTCDateTimeAttribute()
    DataAtualizacao = UTCDateTimeAttribute(null=True)
    Status = UnicodeAttribute()
    User = UnicodeAttribute()
    Analisys_id = UnicodeAttribute()
    Company = UnicodeAttribute()
    Errors = ListAttribute(null=True)

class AnaliseStatusTable(Model):
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "AnaliseStatusTable"
    Id = UnicodeAttribute(hash_key=True)
    DataInicio = UTCDateTimeAttribute()
    DataFinal = UTCDateTimeAttribute()
    DataCriacao = UTCDateTimeAttribute()
    ValidaD100StatusTable = UnicodeAttribute()
    ValidaC500StatusTable = UnicodeAttribute()
    NCMStatusTable = UnicodeAttribute()
    ICMSStatusTable = UnicodeAttribute()
    User = UnicodeAttribute()
    Company = UnicodeAttribute()
    Errors = ListAttribute(null=True)

class ValidaXMLNotaStatusTable(Model):    
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "ValidaXMLNotaStatusTable"
    Id = UnicodeAttribute(hash_key=True)
    IdSPEDFiscal = UnicodeAttribute()
    IdUsuarioAlteracao = UnicodeAttribute()
    DataCriacao = UTCDateTimeAttribute()
    DataAtualizacao = UTCDateTimeAttribute(null=True)
    Status = UnicodeAttribute()
    Errors = ListAttribute(null=True)

class ValidaCFOPStatusTable(Model):
    
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "ValidaCFOPStatusTable"
    Id = UnicodeAttribute(hash_key=True)
    IdSPEDFiscal = UnicodeAttribute()
    IdSPEDContrib = UnicodeAttribute()
    IdUsuarioAlteracao = UnicodeAttribute()
    DataSped = UTCDateTimeAttribute()
    DataCriacao = UTCDateTimeAttribute()
    DataAtualizacao = UTCDateTimeAttribute(null=True)
    Status = UnicodeAttribute()
    Errors = ListAttribute(null=True)
    
class InsumosStatusTable(Model):
    """
    A DynamoDB table
    """
    class Meta:
        table_name = "InsumosStatusTable"
    Id = UnicodeAttribute(hash_key=True)
    Cnpj = UnicodeAttribute()
    DataInicio = UnicodeAttribute()
    DataFim = UnicodeAttribute()
    Key = UnicodeAttribute(null=True)
    Status = UnicodeAttribute()
    Errors = ListAttribute(null=True)
