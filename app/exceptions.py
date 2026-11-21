class PDFNotFoundError(Exception):
    def __init__(self, pdf_id:int):
        self.pdf_id = pdf_id

class InvalidPDFError(Exception):
    def __init__(self, message: str):
        self.message = message

class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

class UserAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email


class DuplicatePDFError(Exception):
    def __init__(self, filename: str):
        self.filename = filename
