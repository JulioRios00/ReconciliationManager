#Services
from common.error_handling import all_exception_handler, flask_parameter_validation_handler
from common.authorization import get_current_user
from common.conexao_banco import get_session
from services.document_api_service import DocumentoApiService
#Libs
from flask import Flask, request
from flask_authorize import Authorize
from flask_parameter_validation import ValidateParameters, Query, Route, Json
from flask_babel import Babel
from flask import jsonify
from typing import Optional
import serverless_wsgi
import os


app = Flask(__name__)
authorize = Authorize(current_user=get_current_user, app=app)
babel = Babel(app)


if 'AWS_SAM_LOCAL' in os.environ and os.environ['AWS_SAM_LOCAL'] == 'true':
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../translations'

ROUTE_PREFIX = '/document'

app.register_error_handler(Exception, all_exception_handler)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['pt', 'en'])

@app.route(ROUTE_PREFIX + '/create/document', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_document(key: str = Json(min_str_length=1, max_str_length=255),
                        document_type_id: str = Json(min_str_length=1, max_str_length=60),
                        descricao: str = Json(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).create_document(key,document_type_id,descricao)


@app.route(ROUTE_PREFIX + '/validate/request', methods=['PUT'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def validate_document(document_id: str = Json(min_str_length=1, max_str_length=255),
                      status: bool = Json()):
    with get_session() as session:
        return DocumentoApiService(session).validate_document(document_id,status)
    

@app.route(ROUTE_PREFIX + '/list/files')
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def list_documents(page: Optional[int] = Query(default=1),
                    per_page: Optional[int] = Query(default=10),
                    document_type_id: str = Query(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).list_document_by_document_type(page,per_page,document_type_id)


@app.route(ROUTE_PREFIX + '/list/document_types')
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def list_document_types(page: Optional[int] = Query(default=1),
                        per_page: Optional[int] = Query(default=10),
                        cnpj: str = Query(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).list_document_type_by_cnpj(cnpj,page,per_page)


@app.route(ROUTE_PREFIX + '/create/document_version', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_document_version(key: str = Json(min_str_length=1, max_str_length=255),
                        latest_document_id: str = Json(min_str_length=1, max_str_length=60),
                        versao: str = Json(min_str_length=1, max_str_length=255)):
    with get_session() as session:
        return DocumentoApiService(session).create_document_version(key,latest_document_id,versao)

@app.route(ROUTE_PREFIX + '/create/document_types', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_document_types(company_id: str = Json(min_str_length=1, max_str_length=60),
                        extensao: str = Json(min_str_length=1, max_str_length=10),
                        nome: str = Json(min_str_length=1, max_str_length=255),
                        sigla: str = Json(min_str_length=1, max_str_length=6)):
    with get_session() as session:
        return DocumentoApiService(session).create_document_types(company_id,extensao,nome,sigla)


@app.route(ROUTE_PREFIX + '/create/tag_document', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_tag_documents(document_id: str = Json(min_str_length=1, max_str_length=60),
                        tag_id: str = Json(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).create_tag_document(document_id, tag_id)


@app.route(ROUTE_PREFIX + '/email/sending', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def send_email(id_documento:  Optional[str] = Json(max_str_length=60),
               list_emails:  Optional[list] = Json(),
               email_subject:  Optional[str] = Json(),
               email_body:  Optional[str] = Json()):
    with get_session() as session:
        return DocumentoApiService(session).send_email(id_documento, list_emails, email_subject, email_body)

@app.route(ROUTE_PREFIX + '/validate_tag', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def validate_tag(tag_id: str = Json(min_str_length=1, max_str_length=60),
                document_id: str = Json(min_str_length=1, max_str_length=60),
                document_type_id: str = Json(min_str_length=1, max_str_length=60),
                validation: bool = Json()):
    with get_session() as session:
        return DocumentoApiService(session).validate_tag_document(document_id,tag_id,validation,document_type_id)
    
@app.route(ROUTE_PREFIX + '/delete/document/<string:id>', methods=['DELETE'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def delete_document(id: str = Route(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).delete_table_document(id)
    
    
@app.route(ROUTE_PREFIX + '/create/palavra_chave', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_palavra_chave(palavra: str = Json(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).create_palavra_chave(palavra)

@app.route(ROUTE_PREFIX + '/create/palavra_chave_documento', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_palavra_chave_documento(id_palavra_chave: str = Json(min_str_length=1, max_str_length=60),
                                   id_documento: str = Json(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).create_palavra_chave_documento(id_palavra_chave, id_documento)
    
    
@app.route(ROUTE_PREFIX + '/list/palavra_chave')
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def list_palavra_chave(page: Optional[int] = Query(default=1),
                        per_page: Optional[int] = Query(default=10)):
    with get_session() as session:
        return DocumentoApiService(session).list_table_palavra_chave(page,per_page)
    
    
@app.route(ROUTE_PREFIX + '/delete/palavra_chave/<string:id>', methods=['DELETE'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def delete_palavra_chave(id: str = Route(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).delete_palavra_chave(id)

@app.route(ROUTE_PREFIX + '/create/documento_anexo', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_documento_anexo(id_documento: str = Json(min_str_length=1, max_str_length=60),
                           id_anexo: str = Json(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).create_doc_anexo(id_documento, id_anexo)

@app.route(ROUTE_PREFIX + '/delete/documento_anexo/<string:id>', methods=['DELETE'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def delete_docum_anexo(id: str = Route(min_str_length=1, max_str_length=60)):
    with get_session() as session:
        return DocumentoApiService(session).delete_doc_anexo(id)
    
    
@app.route(ROUTE_PREFIX + '/create/arquivo_anexo', methods=['POST'])
@authorize.in_group('admin')
@ValidateParameters(flask_parameter_validation_handler)
def create_arquivo_anexo(id_documento: str = Json(min_str_length=1, max_str_length=255),
                         key: str = Json(min_str_length=1, max_str_length=255)):
    with get_session() as session:
        return DocumentoApiService(session).create_aquiv_anexo(id_documento, key)
    
def add_body(event):
    if 'body' not in event:
        event['body'] = '{}'
        headers = event['headers']
        headers['content-type'] = 'application/json'
    return event


def main(event, context):
    event = add_body(event)
    return serverless_wsgi.handle_request(app, event, context)
