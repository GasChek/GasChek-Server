class ServerNameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.server_header = "GasChek"

    def __call__(self, request):
        response = self.get_response(request)
        response["Server"] = self.server_header
        return response
