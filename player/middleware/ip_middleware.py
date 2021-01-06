class XForwardedForMiddleware:
    """
    Set REMOTE_ADDR if it's missing because of a reverse proxy (nginx + gunicorn) deployment.
    https://stackoverflow.com/questions/34251298/empty-remote-addr-value-in-django-application-when-using-nginx-as-reverse-proxy
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            remote_addrs = request.META['HTTP_X_FORWARDED_FOR'].split(',')
            remote_addr = None

            # for some bots, 'unknown' was prepended as the first value: `unknown, ***.***.***.***`
            # in which case the second value actually is the correct one
            for ip in remote_addrs:
                ip = self._validated_ip(ip)
                if ip is not None:
                    remote_addr = ip
                    break

            if remote_addr is None:
                raise SuspiciousOperation('Malformed X-Forwarded-For.')

            request.META['HTTP_X_PROXY_REMOTE_ADDR'] = request.META['REMOTE_ADDR']
            request.META['REMOTE_ADDR'] = remote_addr

        return self.get_response(request)

    def _validated_ip(self, ip):
        ip = ip.strip()
        try:
            validate_ipv46_address(ip)
        except ValidationError:
            return None
        return ip