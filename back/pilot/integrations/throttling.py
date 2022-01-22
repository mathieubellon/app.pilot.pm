from rest_framework.throttling import SimpleRateThrottle


class TokenRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        # request.auth hold the ApiToken instance used to authenticate to the API
        return self.cache_format % {
            'scope': self.scope,
            'ident': request.auth.token
        }


class TokenMinuteRateThrottle(TokenRateThrottle):
    scope = 'token_minute'
    rate = '60/min'


class TokenHourRateThrottle(TokenRateThrottle):
    scope = 'token_hour'
    rate = '1000/hour'
