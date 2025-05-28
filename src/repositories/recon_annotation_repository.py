from sqlalchemy.orm import Session
import uuid
from typing import List, Optional
import logging

from models.schema_ccs import ReconAnnotation
from enums.status_enum import StatusEnum


class ReconAnnotationRepository:
    """Repository for ReconAnnotation model operations"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, reconciliation_id: uuid.UUID, annotation: str, 
               status: Optional[StatusEnum] = None) -> ReconAnnotation:
        """
        Create a new annotation for a reconciliation item
        
        Args:
            reconciliation_id: UUID of the reconciliation item
            annotation: Text of the annotation
            status: Optional status of the annotation
            
        Returns:
            The created ReconAnnotation object
        """
        try:
            new_annotation = ReconAnnotation(
                reconciliation_id=reconciliation_id,
                annotation=annotation,
                status=status
            )
            self.db_session.add(new_annotation)
            self.db_session.commit()
            self.db_session.refresh(new_annotation)
            return new_annotation
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error creating annotation: {str(e)}")
            raise

    def get_by_id(self, annotation_id: uuid.UUID) -> Optional[ReconAnnotation]:
        """
        Get an annotation by its ID

        Args:
            annotation_id: UUID of the annotation

        Returns:
            The ReconAnnotation object if found, None otherwise
        """
        try:
            return self.db_session.query(ReconAnnotation).filter(
                ReconAnnotation.Id == annotation_id,
                ReconAnnotation.Ativo.is_(True),
                ReconAnnotation.Excluido.is_(False)
            ).first()
        except Exception as e:
            logging.error(f"Error getting annotation by ID: {str(e)}")
            raise

    def get_by_reconciliation_id(self, reconciliation_id: uuid.UUID) -> List[ReconAnnotation]:
        """
        Get all annotations for a reconciliation item
        
        Args:
            reconciliation_id: UUID of the reconciliation item
            
        Returns:
            List of ReconAnnotation objects
        """
        try:
            return self.db_session.query(ReconAnnotation).filter(
                ReconAnnotation.ReconciliationId == reconciliation_id,
                ReconAnnotation.Ativo.is_(True),
                ReconAnnotation.Excluido.is_(False)
            ).all()
        except Exception as e:
            logging.error(f"Error getting annotations by reconciliation ID: {str(e)}")
            raise

    def update(self, annotation_id: uuid.UUID, 
               annotation: Optional[str] = None, 
               status: Optional[StatusEnum] = None) -> Optional[ReconAnnotation]:
        """
        Update an annotation
        
        Args:
            annotation_id: UUID of the annotation
            annotation: New text for the annotation (optional)
            status: New status for the annotation (optional)
            
        Returns:
            The updated ReconAnnotation object if found, None otherwise
        """
        try:
            annotation_obj = self.get_by_id(annotation_id)
            if not annotation_obj:
                return None
                
            if annotation is not None:
                annotation_obj.Annotation = annotation
                
            if status is not None:
                annotation_obj.Status = status
                
            self.db_session.commit()
            self.db_session.refresh(annotation_obj)
            return annotation_obj
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error updating annotation: {str(e)}")
            raise

    def delete(self, annotation_id: uuid.UUID) -> bool:
        """
        Soft delete an annotation
        
        Args:
            annotation_id: UUID of the annotation
            
        Returns:
            True if the annotation was deleted, False otherwise
        """
        try:
            annotation_obj = self.get_by_id(annotation_id)
            if not annotation_obj:
                return False
                
            annotation_obj.Ativo = False
            annotation_obj.Excluido = True
            self.db_session.commit()
            return True
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error deleting annotation: {str(e)}")
            raise

    def hard_delete(self, annotation_id: uuid.UUID) -> bool:
        """
        Hard delete an annotation from the database
        
        Args:
            annotation_id: UUID of the annotation
            
        Returns:
            True if the annotation was deleted, False otherwise
        """
        try:
            annotation_obj = self.get_by_id(annotation_id)
            if not annotation_obj:
                return False
                
            self.db_session.delete(annotation_obj)
            self.db_session.commit()
            return True
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error hard deleting annotation: {str(e)}")
            raise
