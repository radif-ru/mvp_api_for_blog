class ViewParseRequestBodyMixin:
    def parse_request_body(self) -> list:
        """ Распарсить тело запроса """
        body: list = self.request.body.decode('utf-8').split('\r\n')
        return body
