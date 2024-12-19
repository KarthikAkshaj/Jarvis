import logging


class ErrorHandler:
    @staticmethod
    def handle_error(error: Exception, context: str = None) -> str:
        """Centralized error handling with logging and user-friendly messages"""
        error_msg = f"Error in {context}: {str(error)}" if context else str(error)
        logging.error(error_msg)

        error_responses = {
            FileNotFoundError: "I couldn't find a required file.",
            PermissionError: "I don't have permission to access a required resource.",
            ConnectionError: "There seems to be a network connection issue.",
            ValueError: "There was an invalid value in the request.",
            KeyError: "A required configuration key is missing.",
            Exception: "An unexpected error occurred.",
        }

        for error_type, response in error_responses.items():
            if isinstance(error, error_type):
                return response

        return "I encountered an unexpected error."
