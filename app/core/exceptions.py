from fastapi import HTTPException, status


class AuthExceptions:
    """Centralized authentication-related exceptions."""

    @staticmethod
    def invalid_credentials() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def invalid_token() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserExceptions:
    """Centralized user-related exceptions."""

    @staticmethod
    def email_already_registered() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    @staticmethod
    def user_not_found() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )


class CategoryExceptions:
    """Centralized category-related exceptions."""

    @staticmethod
    def category_not_found() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    @staticmethod
    def category_update_denied() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own categories."
        )

    @staticmethod
    def category_delete_denied() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own categories."
        )


class TransactionExceptions:
    """Centralized transaction-related exceptions."""

    @staticmethod
    def transaction_not_found() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found."
        )

    @staticmethod
    def transaction_access_denied() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own transactions."
        )

    @staticmethod
    def transaction_update_denied() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own transactions."
        )

    @staticmethod
    def transaction_delete_denied() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own transactions."
        )

    @staticmethod
    def invalid_category() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category ID."
        )
