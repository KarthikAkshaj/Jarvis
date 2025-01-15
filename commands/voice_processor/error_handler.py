from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta


class VoiceCommandError(Exception):
    """Base exception for voice command errors"""

    pass


class CommandNotFoundError(VoiceCommandError):
    """Raised when command is not recognized"""

    pass


class CommandExecutionError(VoiceCommandError):
    """Raised when command execution fails"""

    pass


class CommandPermissionError(VoiceCommandError):
    """Raised when permission is denied"""

    pass


class EnhancedErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_log = []
        self.max_log_size = 100

    def log_error(self, error: Exception, command: str, context: Optional[Dict] = None):
        """Log error with context"""
        error_entry = {
            "timestamp": datetime.now(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "command": command,
            "context": context or {},
        }

        self.error_log.append(error_entry)
        if len(self.error_log) > self.max_log_size:
            self.error_log.pop(0)

        self.logger.error(f"Command error: {error_entry}")

    def get_user_message(self, error: Exception, command: str) -> str:
        """Generate user-friendly error message"""
        if isinstance(error, CommandNotFoundError):
            return "I'm not sure what you want me to do. Could you rephrase that?"
        elif isinstance(error, CommandPermissionError):
            return "I don't have permission to do that. You might need to run me with administrator privileges."
        elif isinstance(error, CommandExecutionError):
            return f"I had trouble executing that command. {str(error)}"

        # Handle other common errors
        error_str = str(error).lower()
        if "not found" in error_str:
            return "I couldn't find what you were looking for. Could you check if it exists?"
        elif "timeout" in error_str:
            return "The operation took too long. Please check your internet connection and try again."
        elif "permission" in error_str:
            return "I don't have permission to do that. Please check your settings."
        elif "connection" in error_str:
            return (
                "I'm having trouble connecting. Please check your internet connection."
            )
        elif "memory" in error_str:
            return "I'm running low on memory. Try closing some applications and try again."
        elif "busy" in error_str:
            return "The system is busy right now. Please try again in a moment."

        return "Something went wrong. Please try again or rephrase your command."

    def get_error_stats(self) -> Dict:
        """Get statistics about recent errors"""
        if not self.error_log:
            return {}

        error_types = {}
        commands_failed = {}
        recent_errors = self.error_log[-10:]  # Last 10 errors

        for entry in self.error_log:
            # Count error types
            error_type = entry["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1

            # Count failed commands
            command = entry["command"]
            commands_failed[command] = commands_failed.get(command, 0) + 1

        return {
            "total_errors": len(self.error_log),
            "error_types": error_types,
            "most_failed_commands": commands_failed,
            "recent_errors": recent_errors,
        }

    def should_retry(self, error: Exception) -> bool:
        """Determine if command should be retried"""
        retriable_errors = [
            "timeout",
            "connection",
            "temporary",
            "busy",
            "retry",
            "again",
        ]

        error_str = str(error).lower()
        return any(err in error_str for err in retriable_errors)

    def clear_old_errors(self, days: int = 7):
        """Clear errors older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        self.error_log = [
            entry for entry in self.error_log if entry["timestamp"] > cutoff_date
        ]

    def get_suggestions(self, error: Exception, command: str) -> List[str]:
        """Get suggestions for fixing the error"""
        suggestions = []
        error_str = str(error).lower()

        if "permission" in error_str:
            suggestions.extend(
                [
                    "Run the application as administrator",
                    "Check your user permissions",
                    "Try using a different account",
                ]
            )
        elif "not found" in error_str:
            suggestions.extend(
                [
                    "Check if the file or application exists",
                    "Verify the path is correct",
                    "Try specifying the full path",
                ]
            )
        elif "connection" in error_str:
            suggestions.extend(
                [
                    "Check your internet connection",
                    "Try again in a few moments",
                    "Verify your network settings",
                ]
            )
        elif "memory" in error_str:
            suggestions.extend(
                [
                    "Close unused applications",
                    "Clear temporary files",
                    "Restart the application",
                ]
            )

        return suggestions
