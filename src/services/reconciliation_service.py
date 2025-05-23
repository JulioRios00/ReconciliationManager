import logging
import traceback
from repositories.ccs_repository import ReconciliationRepository


class ReconciliationService:
    def __init__(self, db_session):
        self.session = db_session
        self.reconciliation_repository = ReconciliationRepository(db_session)

    def get_all_reconciliation_data(self):
        """
        Retrieve all data from the ccs.Reconciliation table using SQLAlchemy

        Returns:
            Dictionary with all reconciliation data
        """
        try:
            records = self.reconciliation_repository.get_all()

            result_list = [record.serialize() for record in records]

            return {"data": result_list}
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(
                f"Exception in get_all_reconciliation_data: {str(e)}"
                )
            logging.error(f"Traceback: {error_details}")

            return {"message":
                    "Failed to retrieve reconciliation data", "error": str(e)
                    }, 501

    def get_paginated_reconciliation_data(
        self,
        limit=100,
        offset=0,
        filter_type='all'
    ):
        """
        Retrieve paginated data from the 
        ccs.Reconciliation table using SQLAlchemy

        Args:
            limit: Number of records to return
            offset: Offset for pagination
            filter_type: Type of filter to apply (
                'all',
                'discrepancies',
                'air_only',
                'cat_only'
                )

        Returns:
            Dictionary with paginated reconciliation data and pagination info
        """
        try:
            if filter_type == 'all':
                records = self.reconciliation_repository.get_paginated(
                    limit,
                    offset
                    )
                total_count = self.reconciliation_repository.get_count()
            else:
                records = (self.reconciliation_repository.
                           get_filtered(filter_type)
                           )
                if limit and offset:
                    records = records[offset:offset+limit]
                total_count = (
                    self.reconciliation_repository.
                    get_filtered_count(filter_type)
                    )

            result_list = [record.serialize() for record in records]

            return {
                "data": result_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "next_offset": (
                        offset + limit if offset + limit < total_count
                        else None
                        )
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(
                f"Exception in get_paginated_reconciliation_data: {str(e)}"
                )
            logging.error(f"Traceback: {error_details}")

            return {"message":
                    "Failed to retrieve reconciliation data", "error": str(e)
                    }, 501

    def get_reconciliation_summary(self):
        """
        Get summary statistics for the reconciliation data using SQLAlchemy

        Returns:
            Dictionary with summary statistics
        """
        try:
            records = self.reconciliation_repository.get_all()

            total_records = len(records)
            matching_records = sum(
                1 for r in records if r.Air == 'Yes' and r.Cat == 'Yes'
                )
            air_only_records = sum(
                1 for r in records if r.Air == 'Yes' and r.Cat == 'No'
                )
            cat_only_records = sum(
                1 for r in records if r.Air == 'No' and r.Cat == 'Yes'
                )
            quantity_discrepancies = sum(
                1 for r in records if r.DifQty == 'Yes'
                )
            price_discrepancies = sum(
                1 for r in records if r.DifPrice == 'Yes'
                )

            total_amount_difference = 0
            for record in records:
                if record.AmountDif and record.AmountDif.strip():
                    try:
                        total_amount_difference += float(record.AmountDif)
                    except (ValueError, TypeError):
                        pass

            return {
                "summary": {
                    "total_records": total_records,
                    "matching_records": matching_records,
                    "air_only_records": air_only_records,
                    "cat_only_records": cat_only_records,
                    "quantity_discrepancies": quantity_discrepancies,
                    "price_discrepancies": price_discrepancies,
                    "total_amount_difference": total_amount_difference
                }
            }
        except Exception as e:
            error_details = traceback.format_exc()
            logging.error(f"Exception in get_reconciliation_summary: {str(e)}")
            logging.error(f"Traceback: {error_details}")

            return {
                "message": "Failed to retrieve reconciliation summary",
                "error": str(e)
                }, 501
