class AppError(Exception):
    # Error codes
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_OTP = "INVALID_OTP"
    EMAIL_EXISTS = "EMAIL_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    MISSING_REFRESH_TOKEN = "MISSING_REFRESH_TOKEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SUPABASE_ERROR = "SUPABASE_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)