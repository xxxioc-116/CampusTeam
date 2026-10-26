from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    details = response.data
    message = details.get("detail", "请求处理失败") if isinstance(details, dict) else "请求处理失败"
    response.data = {
        "code": getattr(exc, "default_code", "request_error"),
        "message": str(message),
        "details": details,
    }
    return response

