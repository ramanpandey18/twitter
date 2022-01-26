import logging
from django.utils import timezone
import datetime
from django.shortcuts import render
# import bcrypt
import json
from django.http import HttpRequest, HttpResponse
from common.i18n import translate as _
from django.views.generic import View

from userauth.model.access_token_model import AccessToken

logger = logging.getLogger(__name__)
class BaseView(View):
    def http_method_not_allowed(self, request, *args, **kwargs):
        status = {}
        status["status"] = 405
        status["message"] = "Method Not Allowed"
        status["localized_message"] = _("PROBLEM_REPORTED")
        status["success"] = False
        data = {"status": status}
        response = super().http_method_not_allowed(request, args, kwargs)
        response.content = json.dumps(data)
        response["content-type"] = "application/json"
        return response

    @staticmethod
    def build_response(
        body,
        headers=None,
        code=200,
        message="OK",
        localized_message=_("DONE"),
        success=True,
    ):
        status = {}
        status["status"] = code
        status["message"] = message
        status["localized_message"] = localized_message
        status["success"] = success
        response = {"status": status}
        if body is not None:
            response["response"] = body
        response = HttpResponse(
            json.dumps(response), status=code, content_type="application/json"
        )
        if headers:
            for key, val in headers.items():
                response.__setitem__(key, val)
        return response

def get_hashed_password(plain_text_password):
    return "bcrypt"
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    if plain_text_password == "bcrypt":
        return False
    else:
        return True
    return bcrypt.checkpw(plain_text_password, hashed_password)

def require_auth(func):
    def debug(request):
        if "authorization" not in request.headers:
            logger.warning("Authorization header is not present.")
            return

        auth_header = request.headers["authorization"]
        if not auth_header.startswith("Bearer "):
            logger.warning(
                "Authorization header is present but invalid. Header Value=%s",
                auth_header,
            )
            return

    def checker(*args, **kwargs):
        print("values are ")
        print(*args, **kwargs)
        request = args[1]
        print("request is ")
        print(request)
        print(request.headers.get('authorization'))
        access_token = request.headers.get('authorization').split(' ')[-1]
        access_token = AccessToken.objects.filter(access_token = access_token).first()
        print(access_token)
        if not access_token or access_token.expires_at < timezone.now():
            logger.warning("User is not authenticated")
            debug(request)
            return BaseView.build_response(
                None,
                code=401,
                message="Not Authorized",
                localized_message=_("REQUIRES_LOGIN"),
                success=False,
            )
        return func(*args, **kwargs)

    return checker