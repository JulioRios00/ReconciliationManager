from app.document_api.document_api import main
from flask import Flask

app = Flask(__name__)

class TestDlmeApi():

    def set_up_api(self, path, http_method, query_param, body):
        return {
            "body": body,
            "resource": "/{proxy+}",
            "path": path,
            "httpMethod": http_method,
            "queryStringParameters": query_param,
            "pathParameters": {
                "proxy": "/path/to/resource"
            },
            "stageVariables": {
                "baz": "qux"
            },
            "headers": {
                "Authorization": "Bearer eyJraWQiOiJ1QUU5c2NXOWo4a09wT1FkK0pjUzRDTlVMcVhiNGg0WUF6cXk0Y2c1dE1ZPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJjNGI4ODQwOC1mMDMxLTcwMTMtMDQ2Ny1iMTI0YjBlYTNjNTIiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9KUndROXk0SmciLCJjbGllbnRfaWQiOiI1dmxpbG90a3I5bXRkcHZiNDdmanY5ZmQ3MyIsIm9yaWdpbl9qdGkiOiJjZTg0Y2FjNi1mMWQ1LTQxZGUtOWU2YS02OGE4ODcxOTA4NDIiLCJldmVudF9pZCI6ImZiYjAyNWI5LTAxYjYtNDRlNC1iMGZhLTAwMGU5NjgwN2RjYyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3MjE0MTA1NzgsImV4cCI6MTcyMjAwNDk2OSwiaWF0IjoxNzIyMDAxMzY5LCJqdGkiOiIyOTI2Mzc5YS05ZTBlLTQyNTEtYjBkZC0yMmI5MWViNWE1ODAiLCJ1c2VybmFtZSI6ImM0Yjg4NDA4LWYwMzEtNzAxMy0wNDY3LWIxMjRiMGVhM2M1MiJ9.GyoDbOsMHuZm5NdYsrLhV_Agk1RT-LDCqKokcUEees6PyXnFWgWHYAunb9FzsSJR91NMA791AfeQWZ1P-VtuNj0hvvzU1iILiN-JMH95oI6N_Nv_8F8oIkx-aXESBi3nu0-i6yAF1NXEjutFTU4FWS9bGHU-ZqWazDltZO98o8mraXJFjaSRHJCgZp7N1gpf4Qp4SSrl8A5v1_N7TNhlPCZMrfJoQNbGRnftZJXL0cA47-MGCj_iB6aXKVREG7ThW-X68aSm_7fcSKfvISYvm5Ll3aeB9mc2kma2TnxEE0N10XUEGw2ZWPcKoVT0wh-QqJ7bj-V0l1U1cJPA6qfOqQ",
                "Content-Type": "application/json",
                "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "pt,en;q=0.8",
                "Cache-Control": "max-age=0",
                "CloudFront-Forwarded-Proto": "https",
                "CloudFront-Is-Desktop-Viewer": "true",
                "CloudFront-Is-Mobile-Viewer": "false",
                "CloudFront-Is-SmartTV-Viewer": "false",
                "CloudFront-Is-Tablet-Viewer": "false",
                "CloudFront-Viewer-Country": "US",
                "Host": "1234567890.execute-api.{dns_suffix}",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Custom User Agent String",
                "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
                "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
                "X-Forwarded-For": "",
                "X-Forwarded-Port": "443",
                "X-Forwarded-Proto": "https"
            },
            "requestContext": {
                "accountId": "123456789012",
                "resourceId": "123456",
                "stage": "prod",
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": None,
                    "cognitoIdentityId": None,
                    "caller": None,
                    "apiKey": None,
                    "sourceIp": "",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": None,
                    "userAgent": "Custom User Agent String",
                    "user": None
                },
                "resourcePath": "/{proxy+}",
                "httpMethod": "POST",
                "apiId": "1234567890"
            },
            "isBase64Encoded": False
            }


    # def test_list_document_types(self) -> None:
    #     query_param = {"cnpj": "76575675675676"}
    #     body = "{\"key\":\"value\"}"
    #     event = self.set_up_api('/document/list/document_types','GET',query_param, body)
    #     with app.app_context():
    #         response = main(event,'')
    #         assert response['statusCode'] == 200

    # def test_list_documents(self) -> None:
    #     query_param = {"document_type_id": "3f0343b5-e8ae-4a22-ba79-e930319b825a"}
    #     body = "{\"key\":\"value\"}"
    #     event = self.set_up_api('/document/list/files','GET',query_param, body)
    #     with app.app_context():
    #         response = main(event,'')
    #         assert response['statusCode'] == 200

    # def test_list_palavra_chave(self) -> None:
    #     query_param = {}
    #     body = "{\"key\":\"value\"}"
    #     event = self.set_up_api('/document/list/palavra_chave','GET',query_param, body)
    #     with app.app_context():
    #         response = main(event,'')
    #         assert response['statusCode'] == 200

    # def test_create_palavra_chave(self) -> None:
    #     query_param = {"cnpj": "76575675675676"}
    #     body = "{\"palavra\":\"value\"}"
    #     event = self.set_up_api('/document/create/palavra_chave','POST',query_param, body)
    #     with app.app_context():
    #         response = main(event,'')
    #         assert response['statusCode'] == 201
            
    # def test_create_doc_anexo(self) -> None:
    #     query_param = {}
    #     body = "{\"id_documento\":\"5f973a97-8155-4266-ae71-3c3b9b9ab708\",\"id_anexo\":\"5f973a97-8155-4266-ae71-3c3b9b9ab123\"}"
    #     event = self.set_up_api('/document/create/documento_anexo','POST',query_param, body)
    #     with app.app_context():
    #         response = main(event,'')
    #         print(response)
    #         assert response['statusCode'] == 201
            
    # def test_delete_doc_anexo(self) -> None:
    #     query_param = {}
    #     body = "{\"file_name\":\"Arion - 20059578000120-Invoices.csv\"}",
    #     event = self.set_up_api('/flights/delete/invoice','DELETE',query_param, body)
    #     with app.app_context():
    #         response = main(event,'')
    #         print(response)
    #         assert response['statusCode'] == 400
            
    def test_delete_doc_anexo(self) -> None:
        query_param = {}
        body = "{\"file_name\":\"Arion - 20059578000120-Invoices.csv\"}",
        event = self.set_up_api('/flights/upload/invoice','DELETE',query_param, body)
        with app.app_context():
            response = main(event,'')
            print(response)
            assert response['statusCode'] == 400
            
            