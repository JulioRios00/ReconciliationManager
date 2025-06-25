# Standard Library Imports
import io
import os
import json
import logging

# Third-Party Library Imports
from flask import Flask, request, jsonify
from flask_authorize import Authorize
from flask_parameter_validation import ValidateParameters, Query, Json, Route
import serverless_wsgi

# Application-Specific Common Utilities
from common.authorization import get_current_user

# Application-Specific Services
from services.analyse_data_services import AnalyseDataServices

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
authorize = Authorize(current_user=get_current_user, app=app)

ROUTE_PREFIX = "/analyse_data_api"


# Get all Air Company Invoice Reports
@app.route(ROUTE_PREFIX + "/compare", methods=["POST"])
@authorize.in_group("admin")
def compare():
    """
    compare
    """
    print("Starting compare function")
    analyse_ata_services = AnalyseDataServices()
    analyse_ata_services.compare_billing_invoice()
    return "200"


def add_body(event):
    if "body" not in event:
        event["body"] = "{}"
        headers = event["headers"]
        headers["content-type"] = "application/json"
    return event


def main(event, context):
    logger.info("Lambda main function started")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    event = add_body(event)
    return serverless_wsgi.handle_request(app, event, context)
