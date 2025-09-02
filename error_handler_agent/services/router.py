"""
router.py - Feedback routing service
"""
import logging
from typing import Dict, Callable, Optional
from ..types import NextAction

logger = logging.getLogger(__name__)


class FeedbackRouter:
    """Routes feedback to appropriate consumers"""
    
    def __init__(self):
        self.pipeline_callback: Optional[Callable] = None
        self.ui_callback: Optional[Callable] = None
        self.ops_callback: Optional[Callable] = None
    
    def route_feedback(self, feedback: Dict, next_action: NextAction):
        """
        Route feedback based on next action
        
        Args:
            feedback: Feedback data to route
            next_action: Next action directive
        """
        # Always send to UI
        if self.ui_callback:
            try:
                self.ui_callback(feedback)
            except Exception as e:
                logger.error(f"UI callback failed: {e}")
        
        # Route based on action
        if next_action == NextAction.RESUME:
            # Send to pipeline for resumption
            if self.pipeline_callback:
                try:
                    self.pipeline_callback({
                        "action": "resume",
                        "feedback": feedback,
                        "context": feedback.get("context_preserved", {})
                    })
                except Exception as e:
                    logger.error(f"Pipeline callback failed: {e}")
        
        elif next_action == NextAction.ESCALATE:
            # Send to ops
            if self.ops_callback:
                try:
                    self.ops_callback({
                        "severity": feedback.get("severity", "unknown"),
                        "error_id": feedback.get("error_id", "unknown"),
                        "details": feedback
                    })
                except Exception as e:
                    logger.error(f"Ops callback failed: {e}")
        
        # Log all feedback
        logger.info(f"Feedback routed: {feedback.get('error_id', 'unknown')} -> {next_action}")
    
    def register_pipeline(self, callback: Callable):
        """Register callback for pipeline feedback"""
        self.pipeline_callback = callback
        logger.debug("Pipeline callback registered")
    
    def register_ui(self, callback: Callable):
        """Register callback for UI feedback"""
        self.ui_callback = callback
        logger.debug("UI callback registered")
    
    def register_ops(self, callback: Callable):
        """Register callback for operations feedback"""
        self.ops_callback = callback
        logger.debug("Ops callback registered")