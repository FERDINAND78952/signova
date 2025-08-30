def direct_health_check_app(environ, start_response):
    """
    A direct WSGI application that bypasses all Django middleware
    and simply returns a 200 OK response with 'OK' as the body.
    
    This is used as a last resort for health checks when other methods fail.
    """
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'OK']