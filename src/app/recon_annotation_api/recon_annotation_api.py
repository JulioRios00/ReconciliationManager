import io
import os
import json

from flask import Flask, request, jsonify
from flask_authorize import Authorize
from flask_parameter_validation import ValidateParameters, Query, Json, Route
import serverless_wsgi

from common.error_handling import all_exception_handler, flask_parameter_validation_handler
from common.conexao_banco import get_session
from common.authorization import get_current_user
from common.custom_exception import CustomException

# Application-Specific Services
from services.recon_annotation_service import ReconAnnotationService


app = Flask(__name__)
authorize = Authorize(current_user=get_current_user, app=app)

ROUTE_PREFIX = "/api/annotations"


@app.route(ROUTE_PREFIX, methods=["POST"])
@authorize.in_group("admin")
@ValidateParameters(flask_parameter_validation_handler)
def create_annotation():
    with get_session() as session:
        try:
            data = request.get_json()

            if not data:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Request body is required",
                            "data": None,
                        }
                    ),
                    400,
                )
            reconciliation_id = data.get("reconciliation_id")
            if not reconciliation_id:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Field 'reconciliation_id' is required "
                            "and cannot be empty",
                            "data": None,
                        }
                    ),
                    400,
                )
            if len(reconciliation_id) < 30 or len(reconciliation_id) > 60:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Field 'reconciliation_id' must be "
                            "between 30 and 60 characters",
                            "data": None,
                        }
                    ),
                    400,
                )
            annotation_text = data.get("annotation")
            if not annotation_text:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Field 'annotation' is required and "
                            "cannot be empty",
                            "data": None,
                        }
                    ),
                    400,
                )

            status = data.get("status")

            annotation_service = ReconAnnotationService(session)
            result = annotation_service.create_annotation(
                reconciliation_id=reconciliation_id,
                annotation_text=annotation_text,
                status=status,
            )

            if result["success"]:
                return jsonify(result), 201
            else:
                status_code = (
                    404 if "not found" in result["error"].lower() else 400
                )
                return jsonify(result), status_code

        except CustomException as e:
            return jsonify(
                {"success": False, "error": str(e), "data": None}
            ), 400
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal server error: {str(e)}",
                        "data": None,
                    }
                ),
                500,
            )


@app.route(
    ROUTE_PREFIX + "/by-reconciliation/<string:reconciliation_id>",
    methods=["GET"]
)
@authorize.in_group("admin")
@ValidateParameters(flask_parameter_validation_handler)
def get_annotations_by_reconciliation(
    reconciliation_id: str = Route(min_str_length=30, max_str_length=60)
):
    with get_session() as session:
        try:
            annotation_service = ReconAnnotationService(session)
            result = annotation_service.get_annotations_by_reconciliation_id(
                reconciliation_id
            )

            if result["success"]:
                return jsonify(result), 200
            else:
                status_code = (
                    404
                    if "not found" in result["error"].lower()
                    else 400
                )
                return jsonify(result), status_code

        except CustomException as e:
            return jsonify(
                {"success": False, "error": str(e), "data": None}
            ), 400
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal server error: {str(e)}",
                        "data": None,
                    }
                ),
                500,
            )


@app.route(ROUTE_PREFIX + "/by-id/<string:annotation_id>", methods=["GET"])
@authorize.in_group("admin")
@ValidateParameters(flask_parameter_validation_handler)
def get_annotation_by_id(
    annotation_id: str = Route(min_str_length=30, max_str_length=60)
):
    with get_session() as session:
        try:
            annotation_service = ReconAnnotationService(session)
            result = annotation_service.get_annotation_by_id(annotation_id)

            if result["success"]:
                return jsonify(result), 200
            else:
                status_code = (
                    404
                    if "not found" in result["error"].lower()
                    else 400
                )
                return jsonify(result), status_code

        except CustomException as e:
            return jsonify(
                {"success": False, "error": str(e), "data": None}
            ), 400
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal server error: {str(e)}",
                        "data": None,
                    }
                ),
                500,
            )


@app.route(ROUTE_PREFIX, methods=["PUT"])
@authorize.in_group("admin")
@ValidateParameters(flask_parameter_validation_handler)
def update_annotation():
    with get_session() as session:
        try:
            data = request.get_json()

            if not data:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Request body is required",
                            "data": None,
                        }
                    ),
                    400,
                )
            annotation_id = data.get("annotation_id")
            if not annotation_id:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Field 'annotation_id' is required and "
                            "cannot be empty",
                            "data": None,
                        }
                    ),
                    400,
                )

            # Add validation for annotation_id length
            if len(annotation_id) < 30 or len(annotation_id) > 60:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Field 'annotation_id' must be "
                            "between 30 and 60 characters",
                            "data": None,
                        }
                    ),
                    400,
                )

            annotation_text = data.get("annotation")
            status = data.get("status")

            if annotation_text is None and status is None:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "At least one field "
                            "'annotation' or 'status' "
                            "must be provided for update",
                            "data": None,
                        }
                    ),
                    400,
                )

            annotation_service = ReconAnnotationService(session)
            result = annotation_service.update_annotation(
                annotation_id=annotation_id,
                annotation_text=annotation_text,
                status=status,
            )

            if result["success"]:
                return jsonify(result), 200
            else:
                status_code = (
                    404 if "not found" in result["error"].lower() else 400
                )
                return jsonify(result), status_code

        except CustomException as e:
            return jsonify(
                {"success": False, "error": str(e), "data": None}
            ), 400
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal server error: {str(e)}",
                        "data": None,
                    }
                ),
                500,
            )


@app.route(ROUTE_PREFIX + "/<string:annotation_id>", methods=["DELETE"])
@authorize.in_group("admin")
@ValidateParameters(flask_parameter_validation_handler)
def delete_annotation(
    annotation_id: str = Route(min_str_length=30, max_str_length=60)
):
    with get_session() as session:
        try:
            annotation_service = ReconAnnotationService(session)
            result = annotation_service.delete_annotation(annotation_id)

            if result["success"]:
                return jsonify(result), 200
            else:
                status_code = (
                    404 if "not found" in result["error"].lower() else 400
                    )
                return jsonify(result), status_code

        except CustomException as e:
            return jsonify(
                {"success": False, "error": str(e), "data": None}
            ), 400
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal server error: {str(e)}",
                        "data": None,
                    }
                ),
                500,
            )


def add_body(event):
    if "body" not in event:
        event["body"] = "{}"
        headers = event["headers"]
        headers["content-type"] = "application/json"
    return event


def main(event, context):
    event = add_body(event)
    return serverless_wsgi.handle_request(app, event, context)
