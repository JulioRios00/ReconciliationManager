import json
from unittest.mock import MagicMock, Mock, patch

import pytest
from botocore.exceptions import ClientError


class TestCustomException:
    """Test cases for CustomException class"""

    def test_custom_exception_default_values(self):
        """Test CustomException with default values"""
        from common.custom_exception import CustomException

        exc = CustomException("Test message")
        assert exc.status_code == 400
        assert exc.is_custom == True

    def test_custom_exception_custom_values(self):
        """Test CustomException with custom values"""
        from common.custom_exception import CustomException

        exc = CustomException("Custom message", status_code=404, is_custom=False)
        assert exc.status_code == 404
        assert exc.is_custom == False
        assert str(exc) == "Custom message"

    def test_custom_exception_message_only(self):
        """Test CustomException with message only"""
        from common.custom_exception import CustomException

        exc = CustomException("Simple message")
        assert exc.message == "Simple message"
        assert exc.status_code == 400
        assert exc.is_custom == True

    def test_custom_exception_to_dict(self):
        """Test to_dict method"""
        from common.custom_exception import CustomException

        exc = CustomException("Test message", status_code=500, is_custom=True)
        result = exc.to_dict()

        expected = {"error": {"message": "Test message", "is_custom": True}}
        assert result == expected

    def test_custom_exception_to_dict_default_custom(self):
        """Test to_dict method with default is_custom value"""
        from common.custom_exception import CustomException

        exc = CustomException("Test message")
        result = exc.to_dict()

        expected = {"error": {"message": "Test message", "is_custom": True}}
        assert result == expected


class TestDefaultReturnMessages:
    """Test cases for default return messages"""

    def test_msg_function(self):
        """Test msg_ function"""
        from common.default_return_messages import msg_

        result = msg_("test message")
        assert result == "test message"

    def test_success_message(self):
        """Test SUCCESS constant"""
        from common.default_return_messages import SUCCESS

        assert SUCCESS == "Request success"

    def test_created_message(self):
        """Test CREATED constant"""
        from common.default_return_messages import CREATED

        assert CREATED == "Created"

    def test_no_content_message(self):
        """Test NO_CONTENT constant"""
        from common.default_return_messages import NO_CONTENT

        assert NO_CONTENT == "No content"

    def test_invalid_input_message(self):
        """Test INVALID_INPUT constant"""
        from common.default_return_messages import INVALID_INPUT

        assert INVALID_INPUT == "Invalid input"

    def test_bad_request_message(self):
        """Test BAD_REQUEST constant"""
        from common.default_return_messages import BAD_REQUEST

        assert BAD_REQUEST == "Bad request"

    def test_unauthorized_message(self):
        """Test UNAUTHORIZED constant"""
        from common.default_return_messages import UNAUTHORIZED

        assert UNAUTHORIZED == "Unauthorized"

    def test_not_found_message(self):
        """Test NOT_FOUND constant"""
        from common.default_return_messages import NOT_FOUND

        assert NOT_FOUND == "Not found"


class TestErrorHandling:
    """Test cases for error handling functions"""

    @patch("common.error_handling.jsonify")
    def test_all_exception_handler_custom_exception(self, mock_jsonify):
        """Test all_exception_handler with CustomException"""
        from common.custom_exception import CustomException
        from common.error_handling import all_exception_handler

        mock_jsonify.return_value = {"error": "test"}
        exc = CustomException("Test error", status_code=404)

        result = all_exception_handler(exc)

        mock_jsonify.assert_called_once_with(exc.to_dict())
        assert result == ({"error": "test"}, 404)

    def test_all_exception_handler_non_custom_exception(self):
        """Test all_exception_handler with non-CustomException"""
        from common.error_handling import all_exception_handler

        exc = ValueError("Test error")

        with pytest.raises(ValueError):
            all_exception_handler(exc)

    def test_flask_parameter_validation_handler(self):
        """Test flask_parameter_validation_handler"""
        from common.custom_exception import CustomException
        from common.error_handling import flask_parameter_validation_handler

        exc = ValueError("Parameter validation error")

        with pytest.raises(CustomException) as exc_info:
            flask_parameter_validation_handler(exc)

        assert str(exc_info.value) == "Parameter validation error"


class TestErrorMessages:
    """Test cases for error message constants"""

    def test_n_function(self):
        """Test N_ function"""
        from common.error_messages import N_

        result = N_("test message")
        assert result == "test message"

    def test_client_constant(self):
        """Test CLIENT constant"""
        from common.error_messages import CLIENT

        assert CLIENT == "Client"

    def test_user_constant(self):
        """Test USER constant"""
        from common.error_messages import USER

        assert USER == "User"

    def test_x_not_found_constant(self):
        """Test X_NOT_FOUND constant"""
        from common.error_messages import X_NOT_FOUND

        assert X_NOT_FOUND == "{0} not found."

    def test_user_belongs_to_deactivated_customer(self):
        """Test USER_BELONGS_TO_DEACTIVATED_CUSTOMER constant"""
        from common.error_messages import USER_BELONGS_TO_DEACTIVATED_CUSTOMER

        assert (
            USER_BELONGS_TO_DEACTIVATED_CUSTOMER
            == "User belongs to a deactivated customer"
        )

    def test_company_does_not_belongs_to_customer(self):
        """Test COMPANY_DOES_NOT_BELONGS_TO_CUSTOMER constant"""
        from common.error_messages import COMPANY_DOES_NOT_BELONGS_TO_CUSTOMER

        assert (
            COMPANY_DOES_NOT_BELONGS_TO_CUSTOMER
            == "Company does not belongs to this customer"
        )

    def test_x_invalid_format_constant(self):
        """Test X_INVALID_FORMAT constant"""
        from common.error_messages import X_INVALID_FORMAT

        assert X_INVALID_FORMAT == "{0} invalid format"

    def test_x_already_exists_constant(self):
        """Test X_ALREADY_EXISTS constant"""
        from common.error_messages import X_ALREADY_EXISTS

        assert X_ALREADY_EXISTS == "{0} already exists"

    def test_x_not_found_icms_constant(self):
        """Test X_NOT_FOUND_ICMS constant"""
        from common.error_messages import X_NOT_FOUND_ICMS

        assert X_NOT_FOUND_ICMS == "{0} not found in table ErroAliquotaIcms."

    def test_x_not_found_cfop_constant(self):
        """Test X_NOT_FOUND_CFOP constant"""
        from common.error_messages import X_NOT_FOUND_CFOP

        assert X_NOT_FOUND_CFOP == "{0} not found in table ErroCfopIcms."

    def test_x_not_found_cnae_constant(self):
        """Test X_NOT_FOUND_CNAE constant"""
        from common.error_messages import X_NOT_FOUND_CNAE

        assert X_NOT_FOUND_CNAE == "{0} not found in table ErroNcmCnae."

    def test_x_not_found_nota_constant(self):
        """Test X_NOT_FOUND_NOTA constant"""
        from common.error_messages import X_NOT_FOUND_NOTA

        assert X_NOT_FOUND_NOTA == "{0} not found in table ErroNcmNota."

    def test_x_invalid_constant(self):
        """Test X_INVALID constant"""
        from common.error_messages import X_INVALID

        assert X_INVALID == "Invalid {0}."


class TestHttpWrapper:
    """Test cases for HTTP wrapper functions"""

    @patch("common.http_wrapper.requests.get")
    def test_get_success_json(self, mock_get):
        """Test get function with JSON response"""
        from common.http_wrapper import get

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = get("http://example.com", {"Authorization": "Bearer token"})

        mock_get.assert_called_once_with(
            "http://example.com", headers={"Authorization": "Bearer token"}
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == {"key": "value"}

    @patch("common.http_wrapper.requests.get")
    def test_get_success_text(self, mock_get):
        """Test get function with text response"""
        from common.http_wrapper import get

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "plain text response"
        mock_get.return_value = mock_response

        result = get("http://example.com", json=False)

        assert result == "plain text response"

    @patch("common.http_wrapper.requests.get")
    def test_get_request_failure(self, mock_get):
        """Test get function with request failure"""
        import requests

        from common.http_wrapper import get

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.RequestException(
            "Connection failed"
        )
        mock_get.return_value = mock_response

        with pytest.raises(requests.RequestException):
            get("http://example.com")

    @patch("common.http_wrapper.requests.post")
    def test_post_success_json(self, mock_post):
        """Test post function with JSON response"""
        from common.http_wrapper import post

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        result = post(
            "http://example.com", {"Content-Type": "application/json"}, {"key": "value"}
        )

        mock_post.assert_called_once_with(
            "http://example.com",
            headers={"Content-Type": "application/json"},
            data={"key": "value"},
        )
        assert result == {"status": "success"}

    @patch("common.http_wrapper.requests.post")
    def test_post_success_text(self, mock_post):
        """Test post function with text response"""
        from common.http_wrapper import post

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "success"
        mock_post.return_value = mock_response

        result = post("http://example.com", json=False)

        assert result == "success"

    @patch("common.http_wrapper.requests.post")
    def test_post_request_failure(self, mock_post):
        """Test post function with request failure"""
        import requests

        from common.http_wrapper import post

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.RequestException(
            "Connection failed"
        )
        mock_post.return_value = mock_response

        with pytest.raises(requests.RequestException):
            post("http://example.com")


class TestLambdaBoto:
    """Test cases for Lambda boto3 wrapper"""

    @patch("common.lambda_boto.client")
    def test_invoke_lambda_async(self, mock_client):
        """Test invoke_lambda_async function"""
        from common.lambda_boto import invoke_lambda_async

        mock_response = {"StatusCode": 202, "Payload": b"{}"}
        mock_client.invoke.return_value = mock_response

        function_name = "test-function"
        input_data = {"key": "value"}

        result = invoke_lambda_async(function_name, input_data)

        mock_client.invoke.assert_called_once_with(
            FunctionName=function_name,
            InvocationType="Event",
            Payload=json.dumps(input_data),
        )
        assert result == mock_response

    @patch("common.lambda_boto.client")
    def test_invoke_lambda_async_empty_payload(self, mock_client):
        """Test invoke_lambda_async with empty payload"""
        from common.lambda_boto import invoke_lambda_async

        mock_response = {"StatusCode": 202, "Payload": b"{}"}
        mock_client.invoke.return_value = mock_response

        result = invoke_lambda_async("test-function", {})

        mock_client.invoke.assert_called_once_with(
            FunctionName="test-function", InvocationType="Event", Payload=json.dumps({})
        )
        assert result == mock_response


class TestS3Wrapper:
    """Test cases for S3 wrapper functions"""

    @patch("common.s3.s3")
    def test_get_file_body_by_event(self, mock_s3):
        """Test get_file_body_by_event function"""
        from common.s3 import get_file_body_by_event

        s3_event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "test-key"},
                    }
                }
            ]
        }

        mock_body = Mock()
        mock_s3.get_object.return_value = {"Body": mock_body}

        result = get_file_body_by_event(s3_event)

        mock_s3.get_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")
        assert result == mock_body

    @patch("common.s3.s3")
    def test_get_file_body_by_sped(self, mock_s3):
        """Test get_file_body_by_sped function"""
        from common.s3 import get_file_body_by_sped

        s3_event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "test-key"},
                    }
                }
            ]
        }

        mock_body = Mock()
        mock_s3.get_object.return_value = {"Body": mock_body, "ContentLength": 1024}

        body, size, key = get_file_body_by_sped(s3_event)

        assert body == mock_body
        assert size == 1024
        assert key == "test-key"

    @patch("common.s3.s3")
    def test_get_file_body_by_key(self, mock_s3):
        """Test get_file_body_by_key function"""
        from common.s3 import get_file_body_by_key

        mock_body = Mock()
        mock_s3.get_object.return_value = {"Body": mock_body, "ContentLength": 2048}

        body, size = get_file_body_by_key("test-key", "test-bucket")

        mock_s3.get_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")
        assert body == mock_body
        assert size == 2048

    @patch("common.s3.s3")
    def test_upload_file(self, mock_s3):
        """Test upload_file function"""
        from common.s3 import upload_file

        upload_file("test-key", "test-bucket", b"test content")

        mock_s3.put_object.assert_called_once_with(
            Bucket="test-bucket", Body=b"test content", Key="test-key"
        )

    @patch("common.s3.s3")
    def test_delete_file(self, mock_s3):
        """Test delete_file function"""
        from common.s3 import delete_file

        delete_file("test-key", "test-bucket")

        mock_s3.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="test-key"
        )

    @patch("common.s3.s3")
    def test_check_obj_exists_true(self, mock_s3):
        """Test check_obj_exists when object exists"""
        from common.s3 import check_obj_exists

        mock_s3.get_object.return_value = {"Body": Mock()}

        result = check_obj_exists("test-key", "test-bucket")

        assert result == True

    @patch("common.s3.s3")
    def test_check_obj_exists_false(self, mock_s3):
        """Test check_obj_exists when object doesn't exist"""
        from common.s3 import check_obj_exists

        error = ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")
        mock_s3.get_object.side_effect = error

        result = check_obj_exists("test-key", "test-bucket")

        assert result == False

    @patch("common.s3.s3")
    def test_check_obj_exists_other_error(self, mock_s3):
        """Test check_obj_exists with other error"""
        from common.s3 import check_obj_exists

        error = ClientError({"Error": {"Code": "AccessDenied"}}, "GetObject")
        mock_s3.get_object.side_effect = error

        result = check_obj_exists("test-key", "test-bucket")

        assert result == True  # Should return True for non-NoSuchKey errors

    @patch("common.s3.s3")
    def test_move_obj(self, mock_s3):
        """Test move_obj function"""
        from common.s3 import move_obj

        mock_response = {"VersionId": "test-version"}
        mock_s3.copy_object.return_value = mock_response

        result = move_obj("test-bucket", "old-key", "new-key")

        mock_s3.copy_object.assert_called_once_with(
            Bucket="test-bucket",
            CopySource={"Bucket": "test-bucket", "Key": "old-key"},
            Key="new-key",
        )
        assert result == mock_response

    @patch("common.s3.s3")
    def test_list_objects(self, mock_s3):
        """Test list_objects function"""
        from common.s3 import list_objects

        mock_response = {"Contents": [{"Key": "file1"}, {"Key": "file2"}]}
        mock_s3.list_objects_v2.return_value = mock_response

        kwargs = {"Bucket": "test-bucket", "Prefix": "folder/"}
        result = list_objects(**kwargs)

        mock_s3.list_objects_v2.assert_called_once_with(**kwargs)
        assert result == mock_response
