import json
from rest_framework.renderers import JSONRenderer

class PrettyJSONRenderer(JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200

        # Default wrapper
        response_data = {
            "status": status_code,
            "message": None,
            "data": None
        }

        if isinstance(data, dict):
            # If "message" is already provided in response, use it
            if "message" in data:
                response_data["message"] = data.get("message")
                response_data["data"] = data.get("data", None)

            # If "errors" come from serializer
            elif "errors" in data:
                response_data["message"] = "Validation Error"
                response_data["data"] = data["errors"]

            # If plain dict returned without message
            else:
                response_data["message"] = "Success" if 200 <= status_code < 300 else "Error"
                response_data["data"] = data

        else:
            # Non-dict response (rare case, list/string)
            response_data["message"] = "Success" if 200 <= status_code < 300 else "Error"
            response_data["data"] = data

        return super().render(response_data, accepted_media_type, renderer_context)
