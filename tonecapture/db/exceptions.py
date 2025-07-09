"""tonecapture.db.exceptions"""


class DatabaseError(Exception):
    """Base exception for database-related errors."""


class RecordNotFoundError(DatabaseError):
    """Raised when a record is not found in the database."""

    def __init__(self, record_id: int, model_name: str):
        self.record_id = record_id
        self.model_name = model_name
        super().__init__(f"{model_name} with ID {record_id} not found.")


class DuplicateRecordError(DatabaseError):
    """Raised when attempting to create a duplicate record."""

    def __init__(self, model_name: str = "Unknown", field: str = "Unknown", value: str = "Unknown"):
        self.model_name = model_name
        self.field = field
        self.value = value
        if model_name != "Unknown":
            super().__init__(
                f"A {model_name} with {field} '{value}' already exists."
            )
        else:
            super().__init__("A duplicate record already exists.")
