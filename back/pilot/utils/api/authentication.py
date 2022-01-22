from rest_framework.authentication import SessionAuthentication


class PilotSessionAuthentication(SessionAuthentication):
    # Returns an arbitrary string to force DRF to send a 401 status instead of 403,
    # so the frontend can detect disconnected sessions.
    def authenticate_header(self, request):
        return 'AUTH'
