import json
from rest_framework.renderers import JSONRenderer

class PrettyJSONRenderer(JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"] if renderer_context else None

        response_data = {
            "status": response.status_code if response else 200,
            "message": "Success" if response and 200 <= response.status_code < 300 else "Error",
        }

        if data is not None and "errors" not in data:
            response_data["data"] = data

        if isinstance(data, dict) and "errors" in data:
            response_data["errors"] = data["errors"]

        return super().render(response_data, accepted_media_type, renderer_context)
