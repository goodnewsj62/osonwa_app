from rest_framework import renderers


class CustomRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        response = self.construct_standard_response(
            data=data, renderer_context=renderer_context
        )

        return super(CustomRenderer, self).render(
            response, accepted_media_type, renderer_context
        )

    def construct_standard_response(self, **kwargs):
        renderer_context = kwargs.get("renderer_context")
        status_code = renderer_context.get("response").status_code

        status = self.status_from_httpcode(status_code)
        data = kwargs.get("data")
        message = data.pop("message", None) if data and "message" in data else None

        response = {
            "status": status,
            "status_code": status_code,
            "data": data,
            "message": message,
        }

        if status_code > 299:  # NOTE: could change this to 399 for this application
            return self.extract_error_message(response)
        return response

    def status_from_httpcode(self, status_code):
        if status_code > 399:
            return "error"
        elif status_code > 299:
            return "redirect"
        return "success"

    def extract_error_message(self, response):
        data = response["data"]
        response["data"] = None

        if response["message"]:  # redirect might contain message already
            return response

        # error message are values of details key in data but
        # sometimes the error message is an array of errors stored as the value of data key
        if isinstance(data, dict):
            detail = data.pop("detail", {})
            detail = detail if isinstance(detail, dict) else {"error": detail}
            response["message"] = {**data, **detail}
        else:
            response["message"] = data

        return response
