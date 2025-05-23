from flask import jsonify
from sqlalchemy import text
import logging
import traceback

class ReconciliationService:
    def __init__(self, db_session):
        self.session = db_session

    def get_all_reconciliation_data(self):
        """
        Retrieve all data from the ccs.Reconciliation table

        Returns:
            JSON response with all reconciliation data
        """
        try:
            query = (
                "SELECT * FROM ccs.\"Reconciliation\" "
                "ORDER BY \"AirFlightDate\", \"AirFlightNo\"")
            results = self.session.execute(text(query))

            result_list = []
            for row in results:
                row_dict = {}
                for column, value in row._mapping.items():
                    if value is not None:
                        row_dict[column] = str(value)
                    else:
                        row_dict[column] = None
                result_list.append(row_dict)

            return {"data": result_list}
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(f"Exception in get_all_reconciliation_data: {str(e)}")
            logging.error(f"Traceback: {error_details}")

            return {"message": "Failed to retrieve reconciliation data", "error": str(e)}, 501