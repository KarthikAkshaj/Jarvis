import logging
from typing import Optional, Dict, Any
import traceback
from datetime import datetime
from pathlib import Path


class ErrorLevel:
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_log_dir = Path("logs/errors")
        self.error_log_dir.mkdir(parents=True, exist_ok=True)

        # Error responses for different types of errors
        self.error_responses = {
            "audio": {
                "default": "I'm having trouble with the audio system.",
                "recording": "I couldn't record audio properly.",
                "playback": "I'm having trouble playing audio.",
                "device": "There seems to be an issue with the audio device.",
            },
            "command": {
                "default": "I couldn't process that command.",
                "not_found": "I don't understand that command.",
                "execution": "I couldn't execute that command.",
                "invalid": "That command doesn't seem to be valid.",
            },
            "system": {
                "default": "I encountered a system error.",
                "permission": "I don't have permission to do that.",
                "resource": "I couldn't access a required resource.",
                "timeout": "The operation timed out.",
            },
            "network": {
                "default": "I'm having trouble connecting to the network.",
                "api": "I couldn't connect to an external service.",
                "timeout": "The network request timed out.",
            },
        }

        # Initialize error tracking
        self.error_counts: Dict[str, int] = {}
        self.last_error_time: Dict[str, datetime] = {}

    def handle_error(
        self,
        error: Exception,
        context: str = "",
        error_type: str = "default",
        level: str = ErrorLevel.ERROR,
    ) -> str:
        """Handle an error and return appropriate response"""
        try:
            # Log the error
            error_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(error)}"
            error_msg = f"Error [{error_id}] in {context}: {str(error)}"

            if level == ErrorLevel.CRITICAL:
                self.logger.critical(error_msg)
            elif level == ErrorLevel.ERROR:
                self.logger.error(error_msg)
            elif level == ErrorLevel.WARNING:
                self.logger.warning(error_msg)
            else:
                self.logger.info(error_msg)

            # Save detailed error info
            self._save_error_details(error_id, error, context, level)

            # Track error frequency
            self._track_error(error_type)

            # Get appropriate response
            response = self._get_error_response(error_type)

            # Add error ID for reference
            response += f" (Error ID: {error_id})"

            return response

        except Exception as e:
            # Fallback error handling
            self.logger.critical(f"Error in error handler: {str(e)}")
            return "I encountered an unexpected error."

    def _save_error_details(
        self, error_id: str, error: Exception, context: str, level: str
    ):
        """Save detailed error information to file"""
        try:
            error_file = self.error_log_dir / f"error_{error_id}.log"
            with open(error_file, "w") as f:
                f.write(f"Error ID: {error_id}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Level: {level}\n")
                f.write(f"Context: {context}\n")
                f.write(f"Error Type: {type(error).__name__}\n")
                f.write(f"Error Message: {str(error)}\n")
                f.write("\nTraceback:\n")
                f.write(traceback.format_exc())

        except Exception as e:
            self.logger.error(f"Error saving error details: {str(e)}")

    def _track_error(self, error_type: str):
        """Track error frequency"""
        now = datetime.now()

        # Update error counts
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1

        # Update last error time
        self.last_error_time[error_type] = now

        # Check for frequent errors
        if self.error_counts[error_type] > 5:
            self.logger.warning(f"Frequent errors of type: {error_type}")

    def _get_error_response(self, error_type: str) -> str:
        """Get appropriate error response"""
        error_category = error_type.split(".")[0]
        error_subtype = error_type.split(".")[1] if "." in error_type else "default"

        if error_category in self.error_responses:
            if error_subtype in self.error_responses[error_category]:
                return self.error_responses[error_category][error_subtype]
            return self.error_responses[error_category]["default"]

        return "I encountered an error while processing your request."

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        return {
            "error_counts": self.error_counts,
            "last_errors": {
                error_type: time.isoformat()
                for error_type, time in self.last_error_time.items()
            },
        }

    @staticmethod
    def format_error_for_user(error: Exception, context: str = "") -> str:
        """Format error message for user display"""
        if isinstance(error, FileNotFoundError):
            return "I couldn't find a required file."
        elif isinstance(error, PermissionError):
            return "I don't have permission to access something I need."
        elif isinstance(error, TimeoutError):
            return "The operation took too long to complete."
        else:
            return f"Something went wrong{f' while {context}' if context else ''}."
