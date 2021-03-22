from typing import Any

from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class UnsupportedMediaTypeException(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(detail=detail, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
