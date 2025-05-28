import uuid
from typing import  Optional, Dict, Any, Tuple
import logging
from sqlalchemy.orm import Session
from repositories.recon_annotation_repository import ReconAnnotationRepository
from models.schema_ccs import Reconciliation
from enums.status_enum import StatusEnum


class ReconAnnotationService:
    """Service class for handling reconciliation annotation business logic"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.annotation_repository = ReconAnnotationRepository(db_session)

    def _validate_uuid(
        self,
        uuid_string: str,
        field_name: str
    ) -> Tuple[bool, Optional[uuid.UUID], Optional[Dict[str, Any]]]:
        """
        Validate UUID format

        Args:
            uuid_string: String to validate as UUID
            field_name: Name of the field for error message

        Returns:
            Tuple of (is_valid, uuid_object, error_response)
        """
        try:
            uuid_obj = uuid.UUID(uuid_string)
            return True, uuid_obj, None
        except ValueError:
            return False, None, {
                "success": False,
                "error": f"Invalid {field_name} format",
                "data": None
            }

    def _validate_annotation_text(
        self,
        annotation_text: Optional[str],
        required: bool = True
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate annotation text

        Args:
            annotation_text: Text to validate
            required: Whether the text is required

        Returns:
            Tuple of (is_valid, error_response)
        """
        if annotation_text is None:
            if required:
                return False, {
                    "success": False,
                    "error": "Annotation text is required",
                    "data": None
                }
            return True, None

        if not annotation_text.strip():
            return False, {
                "success": False,
                "error": "Annotation text cannot be empty",
                "data": None
            }

        return True, None

    def _validate_and_convert_status(
        self,
        status: Optional[str]
    ) -> Tuple[bool, Optional[StatusEnum], Optional[Dict[str, Any]]]:
        """
        Validate and convert status string to StatusEnum

        Args:
            status: Status string to validate

        Returns:
            Tuple of (is_valid, status_enum, error_response)
        """
        if status is None:
            return True, None, None

        try:
            status_enum = StatusEnum(status)
            return True, status_enum, None
        except ValueError:
            return False, None, {
                "success": False,
                "error": f"Invalid status. Valid options are: {
                    [e.value for e in StatusEnum]
                }",
                "data": None
            }

    def _validate_reconciliation_exists(
        self,
        reconciliation_id: uuid.UUID
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate that reconciliation item exists

        Args:
            reconciliation_id: UUID of the reconciliation item

        Returns:
            Tuple of (exists, error_response)
        """
        try:
            reconciliation = self.db_session.query(Reconciliation).filter(
                Reconciliation.Id == reconciliation_id,
                Reconciliation.Ativo is True,
                Reconciliation.Excluido is False
            ).first()

            if reconciliation is None:
                return False, {
                    "success": False,
                    "error": "Reconciliation item not found",
                    "data": None
                }

            return True, None
        except Exception as e:
            logging.error(f"Error checking reconciliation existence: {str(e)}")
            return False, {
                "success": False,
                "error": "Error validating reconciliation item",
                "data": None
            }

    def create_annotation(
        self,
        reconciliation_id: str,
        annotation_text: str,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new annotation for a reconciliation item
        """
        try:
            is_valid, reconciliation_uuid, error = self._validate_uuid(
                reconciliation_id, "reconciliation ID"
            )
            if not is_valid:
                return error

            exists, error = self._validate_reconciliation_exists(
                reconciliation_uuid
            )
            if not exists:
                return error

            is_valid, error = self._validate_annotation_text(
                annotation_text,
                required=True
                )
            if not is_valid:
                return error

            is_valid, status_enum, error = self._validate_and_convert_status(
                status
            )
            if not is_valid:
                return error

            new_annotation = self.annotation_repository.create(
                reconciliation_id=reconciliation_uuid,
                annotation=annotation_text.strip(),
                status=status_enum
            )

            return {
                "success": True,
                "error": None,
                "data": new_annotation.serialize()
            }

        except Exception as e:
            logging.error(f"Error creating annotation: {str(e)}")
            return {
                "success": False,
                "error": "Internal server error while creating annotation",
                "data": None
            }

    def get_annotations_by_reconciliation_id(
        self,
        reconciliation_id: str
    ) -> Dict[str, Any]:
        """
        Get all annotations for a specific reconciliation item
        """
        try:
            is_valid, reconciliation_uuid, error = self._validate_uuid(
                reconciliation_id, "reconciliation ID"
            )
            if not is_valid:
                return error

            annotations = self.annotation_repository.get_by_reconciliation_id(
                reconciliation_uuid
            )
            
            annotations_data = [
                annotation.serialize() for annotation in annotations
            ]

            return {
                "success": True,
                "error": None,
                "data": {
                    "reconciliation_id": reconciliation_id,
                    "annotations": annotations_data,
                    "total_count": len(annotations_data)
                }
            }

        except Exception as e:
            logging.error(f"Error getting annotations: {str(e)}")
            return {
                "success": False,
                "error": "Internal server error while retrieving annotations",
                "data": None
            }

    def get_annotation_by_id(self, annotation_id: str) -> Dict[str, Any]:
        """
        Get a specific annotation by its ID
        """
        try:
            is_valid, annotation_uuid, error = self._validate_uuid(
                annotation_id, "annotation ID"
            )
            if not is_valid:
                return error

            annotation = self.annotation_repository.get_by_id(annotation_uuid)

            if not annotation:
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
            logging.error(f"Error getting annotation by ID: {str(e)}")
            return {
                "success": False,
                "error": "Internal server error while retrieving annotation",
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
        """
        try:
            is_valid, annotation_uuid, error = self._validate_uuid(
                annotation_id, "annotation ID"
            )
            if not is_valid:
                return error

            is_valid, error = self._validate_annotation_text(
                annotation_text,
                required=False
            )
            if not is_valid:
                return error

            is_valid, status_enum, error = self._validate_and_convert_status(
                status
            )
            if not is_valid:
                return error

            updated_annotation = self.annotation_repository.update(
                annotation_id=annotation_uuid,
                annotation=(
                    annotation_text.strip() if annotation_text else None
                ),
                status=status_enum
            )

            if not updated_annotation:
                return {
                    "success": False,
                    "error": "Annotation not found",
                    "data": None
                }

            return {
                "success": True,
                "error": None,
                "data": updated_annotation.serialize()
            }

        except Exception as e:
            logging.error(f"Error updating annotation: {str(e)}")
            return {
                "success": False,
                "error": "Internal server error while updating annotation",
                "data": None
            }

    def delete_annotation(self, annotation_id: str) -> Dict[str, Any]:
        """
        Delete an annotation (soft delete)
        """
        try:
            is_valid, annotation_uuid, error = self._validate_uuid(
                annotation_id, "annotation ID"
            )
            if not is_valid:
                return error

            deleted = self.annotation_repository.delete(annotation_uuid)

            if not deleted:
                return {
                    "success": False,
                    "error": "Annotation not found",
                    "data": None
                }

            return {
                "success": True,
                "error": None,
                "data": {"message": "Annotation deleted successfully"}
            }

        except Exception as e:
            logging.error(f"Error deleting annotation: {str(e)}")
            return {
                "success": False,
                "error": "Internal server error while deleting annotation",
                "data": None
            }
