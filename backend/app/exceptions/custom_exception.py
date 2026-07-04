class OpenAIException(Exception):
    def __init__(self, message: str):

        self.message = message

        super().__init__(message)

class AuthenticationException(Exception):
    def __init__(self, message: str):

        self.message = message

        super().__init__(message) 