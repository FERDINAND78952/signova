# Bad Request (400) Error Fix

## Issue

The application was experiencing HTTP 400 Bad Request errors when deployed on Render, as seen in the logs:

```
Bad Request (400) 
`https://signova.onrender.com/` 
127.0.0.1 - - [30/Aug/2025:12:53:27 +0000] "GET / HTTP/1.1" 400 143 "-" "Go-http-client/2.0" 
127.0.0.1 - - [30/Aug/2025:12:55:20 +0000] "GET / HTTP/1.1" 400 143 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" 
```

## Solution

The following changes were implemented to fix the Bad Request (400) errors:

1. **Custom Bad Request Middleware**
   - Created a new middleware (`BadRequestMiddleware`) to catch and handle HTTP 400 errors
   - Added proper error handling for SuspiciousOperation and DisallowedHost exceptions
   - Implemented user-friendly HTML and JSON responses based on request type

2. **Custom WSGI Handler**
   - Created a custom WSGI handler to catch errors at the WSGI level
   - This provides an additional layer of protection for errors that might occur before reaching Django's middleware

3. **Updated ALLOWED_HOSTS**
   - Added wildcard subdomain for Render (`*.onrender.com`) to ensure all possible Render hostnames are accepted

4. **Health Check Endpoint**
   - Added a dedicated health check endpoint at `/health-check/` for Render's health monitoring
   - Updated the `render.yaml` configuration to use this endpoint

## Files Modified

1. `signova/bad_request_middleware.py` (new file)
2. `signova/wsgi_handler.py` (new file)
3. `signova/settings/base.py` (added middleware)
4. `signova/settings/prod.py` (updated ALLOWED_HOSTS)
5. `signova/wsgi.py` (implemented custom WSGI handler)
6. `signova_app/urls.py` (added health check endpoint)
7. `render.yaml` (updated health check path)

## Testing

To test these changes:

1. Deploy the application to Render
2. Monitor the logs for any remaining 400 errors
3. Test the health check endpoint at `/health-check/`
4. Test the application with various browsers and clients

## Additional Notes

- The custom middleware and WSGI handler will only be active on Render deployments
- All errors are logged to help with debugging any future issues
- The solution provides user-friendly error messages for both API and browser requests