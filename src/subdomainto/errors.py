from typing import Optional

class SubdomainToError(RuntimeError):
    def __init__(self, status_code: int, code: str, message: str, request_id: Optional[str], response_body: str):
        super().__init__(message); self.status_code=status_code; self.code=code; self.request_id=request_id; self.response_body=response_body
class BadRequestError(SubdomainToError): pass
class AuthenticationError(SubdomainToError): pass
class ForbiddenError(SubdomainToError): pass
class NotFoundError(SubdomainToError): pass
class ConflictError(SubdomainToError): pass
class ServerError(SubdomainToError): pass
class TransportError(RuntimeError): pass
class InvalidWebhookError(ValueError): pass
