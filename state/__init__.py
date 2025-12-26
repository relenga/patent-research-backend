"""
Document State Machine Definition

This module defines document states and transition rules as pure data structures.
Phase 2: Enums and data structures ONLY - no execution logic.

The state machine governs document lifecycle from creation to archival,
ensuring valid state progressions and maintaining document integrity.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Set, Optional, List, Any, Union
from dataclasses import dataclass


class DocumentState(Enum):
    """
    Document lifecycle states.
    
    Defines all possible states a document can be in during its lifecycle.
    State progression follows defined transition rules.
    """
    
    # Initial states
    DRAFT = "draft"                    # Document being authored/edited
    PENDING_REVIEW = "pending_review"  # Submitted for review
    
    # Review states  
    IN_REVIEW = "in_review"           # Actively being reviewed
    REVIEW_APPROVED = "review_approved" # Review completed successfully
    REVIEW_REJECTED = "review_rejected" # Review failed, needs changes
    
    # Publication states
    PENDING_PUBLISH = "pending_publish" # Approved, waiting to publish
    PUBLISHED = "published"            # Live and accessible
    
    # Modification states
    PENDING_UPDATE = "pending_update"  # Published doc being updated
    UPDATE_IN_REVIEW = "update_in_review" # Update under review
    
    # Terminal states
    ARCHIVED = "archived"             # No longer active, preserved
    DELETED = "deleted"               # Soft deleted, recoverable
    PERMANENTLY_DELETED = "permanently_deleted" # Hard deleted


class TransitionTrigger(Enum):
    """
    Events that can trigger state transitions.
    
    Represents user actions or system events that cause state changes.
    """
    
    # Author actions
    SUBMIT_FOR_REVIEW = "submit_for_review"
    SAVE_DRAFT = "save_draft" 
    REQUEST_CHANGES = "request_changes"
    
    # Reviewer actions
    START_REVIEW = "start_review"
    APPROVE_REVIEW = "approve_review"
    REJECT_REVIEW = "reject_review"
    
    # Publisher actions
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    
    # Update actions
    REQUEST_UPDATE = "request_update"
    SUBMIT_UPDATE = "submit_update"
    APPROVE_UPDATE = "approve_update"
    REJECT_UPDATE = "reject_update"
    
    # Administrative actions
    ARCHIVE = "archive"
    DELETE = "delete"
    PERMANENTLY_DELETE = "permanently_delete"
    RESTORE = "restore"


@dataclass(frozen=True)
class StateTransition:
    """
    Represents a single state transition rule.
    
    Pure data structure - no execution logic.
    """
    from_state: DocumentState
    trigger: TransitionTrigger
    to_state: DocumentState
    required_permissions: Set[str]
    preconditions: Set[str]
    postconditions: Set[str]


# Document State Transition Rules Table
# Phase 2: Pure data structure - NO execution logic
DOCUMENT_STATE_TRANSITIONS: Dict[DocumentState, Dict[TransitionTrigger, StateTransition]] = {
    
    # DRAFT state transitions
    DocumentState.DRAFT: {
        TransitionTrigger.SUBMIT_FOR_REVIEW: StateTransition(
            from_state=DocumentState.DRAFT,
            trigger=TransitionTrigger.SUBMIT_FOR_REVIEW,
            to_state=DocumentState.PENDING_REVIEW,
            required_permissions={"author", "submit"},
            preconditions={"has_content", "has_title", "author_authenticated"},
            postconditions={"review_requested", "author_notified"}
        ),
        TransitionTrigger.SAVE_DRAFT: StateTransition(
            from_state=DocumentState.DRAFT,
            trigger=TransitionTrigger.SAVE_DRAFT,
            to_state=DocumentState.DRAFT,
            required_permissions={"author", "edit"},
            preconditions={"author_authenticated"},
            postconditions={"draft_saved", "last_modified_updated"}
        ),
        TransitionTrigger.DELETE: StateTransition(
            from_state=DocumentState.DRAFT,
            trigger=TransitionTrigger.DELETE,
            to_state=DocumentState.DELETED,
            required_permissions={"author", "delete"},
            preconditions={"author_authenticated"},
            postconditions={"soft_deleted", "recoverable"}
        ),
    },
    
    # PENDING_REVIEW state transitions
    DocumentState.PENDING_REVIEW: {
        TransitionTrigger.START_REVIEW: StateTransition(
            from_state=DocumentState.PENDING_REVIEW,
            trigger=TransitionTrigger.START_REVIEW,
            to_state=DocumentState.IN_REVIEW,
            required_permissions={"reviewer", "start_review"},
            preconditions={"reviewer_assigned", "reviewer_authenticated"},
            postconditions={"review_started", "author_notified", "reviewer_assigned_to_doc"}
        ),
        TransitionTrigger.REQUEST_CHANGES: StateTransition(
            from_state=DocumentState.PENDING_REVIEW,
            trigger=TransitionTrigger.REQUEST_CHANGES,
            to_state=DocumentState.DRAFT,
            required_permissions={"author", "edit"},
            preconditions={"author_authenticated"},
            postconditions={"returned_to_draft", "review_cancelled"}
        ),
    },
    
    # IN_REVIEW state transitions
    DocumentState.IN_REVIEW: {
        TransitionTrigger.APPROVE_REVIEW: StateTransition(
            from_state=DocumentState.IN_REVIEW,
            trigger=TransitionTrigger.APPROVE_REVIEW,
            to_state=DocumentState.REVIEW_APPROVED,
            required_permissions={"reviewer", "approve"},
            preconditions={"reviewer_authenticated", "review_complete"},
            postconditions={"review_approved", "author_notified", "ready_for_publish"}
        ),
        TransitionTrigger.REJECT_REVIEW: StateTransition(
            from_state=DocumentState.IN_REVIEW,
            trigger=TransitionTrigger.REJECT_REVIEW,
            to_state=DocumentState.REVIEW_REJECTED,
            required_permissions={"reviewer", "reject"},
            preconditions={"reviewer_authenticated", "rejection_reason_provided"},
            postconditions={"review_rejected", "author_notified", "feedback_provided"}
        ),
    },
    
    # REVIEW_APPROVED state transitions
    DocumentState.REVIEW_APPROVED: {
        TransitionTrigger.PUBLISH: StateTransition(
            from_state=DocumentState.REVIEW_APPROVED,
            trigger=TransitionTrigger.PUBLISH,
            to_state=DocumentState.PUBLISHED,
            required_permissions={"publisher", "publish"},
            preconditions={"publisher_authenticated", "approved_for_publish"},
            postconditions={"published", "publicly_accessible", "author_notified"}
        ),
        TransitionTrigger.REQUEST_CHANGES: StateTransition(
            from_state=DocumentState.REVIEW_APPROVED,
            trigger=TransitionTrigger.REQUEST_CHANGES,
            to_state=DocumentState.DRAFT,
            required_permissions={"author", "edit"},
            preconditions={"author_authenticated"},
            postconditions={"returned_to_draft", "approval_revoked"}
        ),
    },
    
    # REVIEW_REJECTED state transitions
    DocumentState.REVIEW_REJECTED: {
        TransitionTrigger.REQUEST_CHANGES: StateTransition(
            from_state=DocumentState.REVIEW_REJECTED,
            trigger=TransitionTrigger.REQUEST_CHANGES,
            to_state=DocumentState.DRAFT,
            required_permissions={"author", "edit"},
            preconditions={"author_authenticated"},
            postconditions={"returned_to_draft", "rejection_acknowledged"}
        ),
    },
    
    # PUBLISHED state transitions
    DocumentState.PUBLISHED: {
        TransitionTrigger.REQUEST_UPDATE: StateTransition(
            from_state=DocumentState.PUBLISHED,
            trigger=TransitionTrigger.REQUEST_UPDATE,
            to_state=DocumentState.PENDING_UPDATE,
            required_permissions={"author", "request_update"},
            preconditions={"author_authenticated", "update_needed"},
            postconditions={"update_requested", "version_locked"}
        ),
        TransitionTrigger.ARCHIVE: StateTransition(
            from_state=DocumentState.PUBLISHED,
            trigger=TransitionTrigger.ARCHIVE,
            to_state=DocumentState.ARCHIVED,
            required_permissions={"admin", "archive"},
            preconditions={"admin_authenticated", "archive_reason_provided"},
            postconditions={"archived", "no_longer_accessible", "preserved"}
        ),
        TransitionTrigger.UNPUBLISH: StateTransition(
            from_state=DocumentState.PUBLISHED,
            trigger=TransitionTrigger.UNPUBLISH,
            to_state=DocumentState.DRAFT,
            required_permissions={"publisher", "unpublish"},
            preconditions={"publisher_authenticated", "unpublish_reason_provided"},
            postconditions={"unpublished", "no_longer_accessible", "returned_to_draft"}
        ),
    },
    
    # PENDING_UPDATE state transitions
    DocumentState.PENDING_UPDATE: {
        TransitionTrigger.SUBMIT_UPDATE: StateTransition(
            from_state=DocumentState.PENDING_UPDATE,
            trigger=TransitionTrigger.SUBMIT_UPDATE,
            to_state=DocumentState.UPDATE_IN_REVIEW,
            required_permissions={"author", "submit_update"},
            preconditions={"author_authenticated", "update_content_ready"},
            postconditions={"update_submitted", "reviewer_notified"}
        ),
    },
    
    # UPDATE_IN_REVIEW state transitions
    DocumentState.UPDATE_IN_REVIEW: {
        TransitionTrigger.APPROVE_UPDATE: StateTransition(
            from_state=DocumentState.UPDATE_IN_REVIEW,
            trigger=TransitionTrigger.APPROVE_UPDATE,
            to_state=DocumentState.PUBLISHED,
            required_permissions={"reviewer", "approve_update"},
            preconditions={"reviewer_authenticated", "update_review_complete"},
            postconditions={"update_approved", "published_version_updated", "author_notified"}
        ),
        TransitionTrigger.REJECT_UPDATE: StateTransition(
            from_state=DocumentState.UPDATE_IN_REVIEW,
            trigger=TransitionTrigger.REJECT_UPDATE,
            to_state=DocumentState.PENDING_UPDATE,
            required_permissions={"reviewer", "reject_update"},
            preconditions={"reviewer_authenticated", "rejection_reason_provided"},
            postconditions={"update_rejected", "author_notified", "feedback_provided"}
        ),
    },
    
    # ARCHIVED state transitions
    DocumentState.ARCHIVED: {
        TransitionTrigger.RESTORE: StateTransition(
            from_state=DocumentState.ARCHIVED,
            trigger=TransitionTrigger.RESTORE,
            to_state=DocumentState.PUBLISHED,
            required_permissions={"admin", "restore"},
            preconditions={"admin_authenticated", "restore_reason_provided"},
            postconditions={"restored", "publicly_accessible", "archive_removed"}
        ),
        TransitionTrigger.PERMANENTLY_DELETE: StateTransition(
            from_state=DocumentState.ARCHIVED,
            trigger=TransitionTrigger.PERMANENTLY_DELETE,
            to_state=DocumentState.PERMANENTLY_DELETED,
            required_permissions={"admin", "permanent_delete"},
            preconditions={"admin_authenticated", "confirmation_provided", "retention_period_expired"},
            postconditions={"permanently_deleted", "data_destroyed", "irreversible"}
        ),
    },
    
    # DELETED state transitions
    DocumentState.DELETED: {
        TransitionTrigger.RESTORE: StateTransition(
            from_state=DocumentState.DELETED,
            trigger=TransitionTrigger.RESTORE,
            to_state=DocumentState.DRAFT,
            required_permissions={"author", "restore"},
            preconditions={"author_authenticated", "within_recovery_window"},
            postconditions={"restored", "returned_to_draft", "deletion_removed"}
        ),
        TransitionTrigger.PERMANENTLY_DELETE: StateTransition(
            from_state=DocumentState.DELETED,
            trigger=TransitionTrigger.PERMANENTLY_DELETE,
            to_state=DocumentState.PERMANENTLY_DELETED,
            required_permissions={"admin", "permanent_delete"},
            preconditions={"admin_authenticated", "retention_period_expired"},
            postconditions={"permanently_deleted", "data_destroyed", "irreversible"}
        ),
    },
}


# Valid Starting States
# Phase 2: Pure data structure
VALID_INITIAL_STATES: Set[DocumentState] = {
    DocumentState.DRAFT
}


# Terminal States (no outgoing transitions except administrative)
# Phase 2: Pure data structure
TERMINAL_STATES: Set[DocumentState] = {
    DocumentState.PERMANENTLY_DELETED
}


# States requiring special permissions
# Phase 2: Pure data structure
ADMINISTRATIVE_STATES: Set[DocumentState] = {
    DocumentState.ARCHIVED,
    DocumentState.DELETED,
    DocumentState.PERMANENTLY_DELETED
}


# State categories for business logic (Phase 3)
# Phase 2: Pure data structure
STATE_CATEGORIES: Dict[str, Set[DocumentState]] = {
    "editable": {
        DocumentState.DRAFT,
        DocumentState.REVIEW_REJECTED,
        DocumentState.PENDING_UPDATE
    },
    "review_required": {
        DocumentState.PENDING_REVIEW,
        DocumentState.IN_REVIEW,
        DocumentState.UPDATE_IN_REVIEW
    },
    "published": {
        DocumentState.PUBLISHED
    },
    "archived": {
        DocumentState.ARCHIVED,
        DocumentState.DELETED,
        DocumentState.PERMANENTLY_DELETED
    }
}


class StateValidationContract(ABC):
    """
    Abstract interface for state machine validation.
    
    Phase 2: Interface contract only - no implementation.
    Validation logic deferred to Phase 3.
    """
    
    @abstractmethod
    def is_valid_transition(
        self,
        from_state: DocumentState,
        trigger: TransitionTrigger,
        to_state: DocumentState
    ) -> bool:
        """
        Validate if state transition is allowed.
        
        Args:
            from_state: Current state
            trigger: Transition trigger
            to_state: Target state
            
        Returns:
            True if transition is valid
        """
        pass
    
    @abstractmethod
    def get_valid_transitions(
        self,
        current_state: DocumentState
    ) -> List[StateTransition]:
        """
        Get all valid transitions from current state.
        
        Args:
            current_state: Current document state
            
        Returns:
            List of valid state transitions
        """
        pass
    
    @abstractmethod
    def validate_preconditions(
        self,
        transition: StateTransition,
        context: Dict[str, Any]
    ) -> bool:
        """
        Validate transition preconditions.
        
        Args:
            transition: State transition to validate
            context: Execution context for validation
            
        Returns:
            True if preconditions are met
        """
        pass
    
    @abstractmethod
    def validate_permissions(
        self,
        transition: StateTransition,
        user_permissions: Set[str]
    ) -> bool:
        """
        Validate user has required permissions for transition.
        
        Args:
            transition: State transition to validate
            user_permissions: User's current permissions
            
        Returns:
            True if permissions are sufficient
        """
        pass