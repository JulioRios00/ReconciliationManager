from sqlalchemy.orm import Session
import uuid
from typing import Dict, Any, Optional
import logging

from repositories.recon_annotation_repository import ReconAnnotationRepository
from repositories.ccs_repository import ReconciliationRepository
from enums.status_enum import StatusEnum
from models.schema_ccs import Reconciliation


logger = logging.getLogger(__name__)


class ReconAnnotationService:
    """Service layer for reconciliation annotations"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.annotation_repository = ReconAnnotationRepository(db_session)
        self.reconciliation_repository = ReconciliationRepository(db_session)

    def _validate_status(self, status: str) -> Dict[str, Any]:
        """
        Validate status enum value
        
        Args:
            status: Status string to validate
            
        Returns:
            Dictionary with validation result
        """
        if status is None:
            return {"valid": True, "enum_value": None}
        
        try:
            enum_value = StatusEnum(status)
            return {"valid": True, "enum_value": enum_value}
        except ValueError:
            valid_statuses = [e.value for e in StatusEnum]
            error_msg = (
                f"Invalid status. Valid options are: "
                f"{', '.join(valid_statuses)}"
            )
            logger.error(f"Status validation failed: {error_msg}")
            return {
                "valid": False,
                "error": error_msg
            }

    def create_annotation(
        self,
        reconciliation_id: str,
        annotation_text: str,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new annotation for a reconciliation item

        Args:
            reconciliation_id: UUID of the reconciliation item
            annotation_text: Text of the annotation
            status: Optional status of the annotation

        Returns:
            Dictionary with operation result
        """

        try:
            try:
                reconciliation_uuid = uuid.UUID(reconciliation_id)
            except ValueError as e:
                logger.error(
                    f"Invalid UUID format: {reconciliation_id}, error: {e}"
                )
                return {
                    "success": False,
                    "error": "Invalid reconciliation_id format",
                    "data": None
                }

            reconciliation = self.db_session.query(Reconciliation).filter(
                Reconciliation.Id == reconciliation_uuid,
                Reconciliation.Ativo.is_(True),
                Reconciliation.Excluido.is_(False)
            ).first()

            if not reconciliation:
                logger.error(
                    f"Reconciliation item not found: {reconciliation_uuid}"
                )
                return {
                    "success": False,
                    "error": "Reconciliation item not found",
                    "data": None
                }

            if status is not None:
                status_validation = self._validate_status(status)
                if not status_validation["valid"]:
                    return {
                        "success": False,
                        "error": status_validation["error"],
                        "data": None
                    }
                status_enum = status_validation["enum_value"]
            else:
                status_enum = None

            annotation = self.annotation_repository.create(
                reconciliation_id=reconciliation_uuid,
                annotation=annotation_text,
                status=status_enum
            )

            return {
                "success": True,
                "error": None,
                "data": annotation.serialize()
            }

        except Exception as e:
            logger.error(f"Error creating annotation: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to create annotation: {str(e)}",
                "data": None
            }

    def get_annotation_by_id(self, annotation_id: str) -> Dict[str, Any]:
        """
        Get an annotation by its ID

        Args:
            annotation_id: UUID of the annotation

        Returns:
            Dictionary with operation result
        """
        try:
            try:
                annotation_uuid = uuid.UUID(annotation_id)
            except ValueError:
                logger.error(f"Invalid annotation UUID format: {annotation_id}")
                return {
                    "success": False,
                    "error": "Invalid annotation_id format",
                    "data": None
                }


            annotation = self.annotation_repository.get_by_id(annotation_uuid)
            if not annotation:
                logger.error(f"Annotation not found: {annotation_uuid}")
                return {
                    "success": False,
                    "error": "Annotation not found",
                    "data": None
                }

            return {
                "success": True,
                "error": None,
                "data": annotation.serialize()
            }

        except Exception as e:
            logger.error(f"Error getting annotation: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "Failed to get annotation",
                "data": None
            }

    def get_annotations_by_reconciliation_id(
        self,
        reconciliation_id: str
    ) -> Dict[str, Any]:
        """
        Get all annotations for a reconciliation item

        Args:
            reconciliation_id: UUID of the reconciliation item

        Returns:
            Dictionary with operation result
        """
        try:
            try:
                reconciliation_uuid = uuid.UUID(reconciliation_id)
            except ValueError:
                logger.error(
                    f"Invalid reconciliation UUID format: {reconciliation_id}"
                )
                return {
                    "success": False,
                    "error": "Invalid reconciliation_id format",
                    "data": None
                }

            reconciliation = self.db_session.query(Reconciliation).filter(
                Reconciliation.Id == reconciliation_uuid,
                Reconciliation.Ativo.is_(True),
                Reconciliation.Excluido.is_(False)
            ).first()

            if not reconciliation:
                logger.error(
                    f"Reconciliation item not found: {reconciliation_uuid}"
                )
                return {
                    "success": False,
                    "error": "Reconciliation item not found",
                    "data": None
                }

            annotations = self.annotation_repository.get_by_reconciliation_id(
                reconciliation_uuid
            )

            return {
                "success": True,
                "error": None,
                "data": {
                    "reconciliation_id": reconciliation_id,
                    "annotations": [
                        annotation.serialize() for annotation in annotations
                    ],
                    "total_count": len(annotations)
                }
            }

        except Exception as e:
            logger.error(f"Error getting annotations: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "Failed to get annotations",
                "data": None
            }

    def update_annotation(
        self, 
        annotation_id: str, 
        annotation_text: Optional[str] = None, 
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing annotation
        
        Args:
            annotation_id: UUID of the annotation
            annotation_text: New text for the annotation (optional)
            status: New status for the annotation (optional)
            
        Returns:
            Dictionary with operation result
        """
        try:
            try:
                annotation_uuid = uuid.UUID(annotation_id)
            except ValueError:
                logger.error(
                    f"Invalid annotation UUID format: {annotation_id}"
                )
                return {
                    "success": False,
                    "error": "Invalid annotation_id format",
                    "data": None
                }

            status_enum = None
            if status is not None:
                status_validation = self._validate_status(status)
                if not status_validation["valid"]:
                    return {
                        "success": False,
                        "error": status_validation["error"],
                        "data": None
                    }
                status_enum = status_validation["enum_value"]

            annotation = self.annotation_repository.update(
                annotation_id=annotation_uuid,
                annotation=annotation_text,
                status=status_enum
            )

            if not annotation:
                logger.error(
                    f"Annotation not found for update: {annotation_uuid}"
                )
                return {
                    "success": False,
                    "error": "Annotation not found",
                    "data": None
                }

            return {
                "success": True,
                "error": None,
                "data": annotation.serialize()
            }

        except Exception as e:
            logger.error(f"Error updating annotation: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "Failed to update annotation",
                "data": None
            }

    def delete_annotation(self, annotation_id: str) -> Dict[str, Any]:
        """
        Delete an annotation (soft delete)
        
        Args:
            annotation_id: UUID of the annotation
            
        Returns:
            Dictionary with operation result
        """
        try:
            try:
                annotation_uuid = uuid.UUID(annotation_id)
            except ValueError:
                logger.error(
                    f"Invalid annotation UUID format: {annotation_id}"
                )
                return {
                    "success": False,
                    "error": "Invalid annotation_id format",
                    "data": None
                }

            success = self.annotation_repository.delete(annotation_uuid)

            if not success:
                logger.error(
                    f"Annotation not found for deletion: {annotation_uuid}"
                )
                return {
                    "success": False,
                    "error": "Annotation not found",
                    "data": None
                }

            return {
                "success": True,
                "error": None,
                "data": {
                    "message": "Annotation deleted successfully"
                }
            }

        except Exception as e:
            logger.error(f"Error deleting annotation: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "Failed to delete annotation",
                "data": None
            }
