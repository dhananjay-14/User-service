from fastapi import HTTPException, status

class EntityNotFound(HTTPException):
    """
    Exception for handling entity not found errors (404).
    
    Args:
        name (str): Entity name that wasn't found
    """
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name} not found"
        )


class DuplicateEntity(HTTPException):
    """
    Exception for handling duplicate entity conflicts (409).
    
    Args:
        name (str): Entity name that has a duplicate
        key (str): The field that caused the conflict
    """
    def __init__(self, name: str, key: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{name} with the same {key} already exists"
        )
