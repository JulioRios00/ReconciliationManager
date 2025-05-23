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
            Dictionary with all reconciliation data
        """
        try:
            query = (
                "SELECT * FROM ccs.\"Reconciliation\" "
                "ORDER BY \"AirFlightDate\", \"AirFlightNo\""
            )
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
            logging.error(
                f"Exception in get_all_reconciliation_data: {str(e)}"
            )
            logging.error(f"Traceback: {error_details}")

            return {
                "message": "Failed to retrieve reconciliation data",
                "error": str(e)
            }, 501

    def get_paginated_reconciliation_data(self, limit=100, offset=0):
        """
        Retrieve paginated data from the ccs.Reconciliation table
        """
        try:
            query = (
                "SELECT * FROM ccs.\"Reconciliation\" ORDER BY \"AirFlightDate\", "
                " \"AirFlightNo\" LIMIT :limit OFFSET :offset"
            )
            results = self.session.execute(text(query), {
                "limit": limit,
                "offset": offset
                }
            )

            result_list = []
            for row in results:
                row_dict = {}
                for column, value in row._mapping.items():
                    if value is not None:
                        row_dict[column] = str(value)
                    else:
                        row_dict[column] = None
                result_list.append(row_dict)

            count_query = "SELECT COUNT(*) FROM ccs.\"Reconciliation\""
            total_count = self.session.execute(text(count_query)).scalar()

            return {
                "data": result_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "next_offset": (offset + limit
                                    if offset + limit < total_count
                                    else None)
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(
                f"Exception in get_all_reconciliation_data: {str(e)}"
            )
            logging.error(f"Traceback: {error_details}")

            return {
                "message": "Failed to retrieve reconciliation data",
                "error": str(e)
            }, 501
