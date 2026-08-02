"""Authentication primitives owned by the accounts module."""

from rest_framework.authentication import SessionAuthentication


class CsrfSessionAuthentication(SessionAuthentication):
    """Require a CSRF token for every unsafe API request, including anonymous ones.

    DRF's built-in ``SessionAuthentication`` only performs the check after it
    finds an authenticated user. Registration, login and password-reset
    requests are anonymous, so relying on it alone would leave those browser
    entry points open to login CSRF.
    """

    def authenticate(self, request):
        self.enforce_csrf(request)

        user = getattr(request._request, "user", None)
        if user is None or not user.is_active:
            return None

        return (user, None)
