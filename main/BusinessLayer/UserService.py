import json
import logging
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from main.helpers.custom import CustomJsonResponse
from main.helpers.factory import DataFactory

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod 
    def signup(request):
        try:
            data = json.loads(request.body)
            username = data["username"]
            password = data["password"]
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            email = data["email"]

            um = DataFactory.get_user_manager()
            if um.get_user(username):
                return CustomJsonResponse(data=None, status="failed", error="Username already exists")
            user = um.create_user(username=username,password=password,first_name=first_name,last_name=last_name,email=email,)
            return CustomJsonResponse(data={"user_id": user.id})            

        except Exception as e:
            logger.exception("Signup failed")
            return CustomJsonResponse(data=None, status="failed", error=str(e))

    @staticmethod
    def login(request):
        try:
            data = json.loads(request.body)
            username = data["username"]
            password = data["password"]
            user = authenticate(request,username=username,password=password,)
            if user is None:
                return CustomJsonResponse(data=None, status="failed", error="Invalid username or password")

            login(request, user)
            return CustomJsonResponse()
        except Exception as e:
            logger.exception("Login failed")
            return CustomJsonResponse(data=None, status="failed", error=str(e))

    @staticmethod
    def logout(request):
        logout(request)
        return CustomJsonResponse()

    @staticmethod
    def get_profile(request):
        if not request.user.is_authenticated:
            return CustomJsonResponse(data=None, status="failed", error="Not logged in")
        um = DataFactory.get_user_manager()
        profile = um.get_profile(request.user)

        return CustomJsonResponse(data={
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,

            "phone": profile.phone,
            "address": profile.address,
            "city": profile.city,
            "state": profile.state,
            "pincode": profile.pincode,
        })

    @staticmethod
    def update_profile(request):
        try:
            if not request.user.is_authenticated:
                return CustomJsonResponse(data=None, status="failed", error="Not logged in")
            data = json.loads(request.body)
            request.user.first_name = data.get("first_name",request.user.first_name,)
            request.user.last_name = data.get("last_name",request.user.last_name,)
            request.user.email = data.get("email",request.user.email,)
            request.user.save()

            um = DataFactory.get_user_manager()
            um.update_profile(request.user,data,)
            return CustomJsonResponse()

        except Exception as e:
            logger.exception("Profile update failed")
            return CustomJsonResponse(data=None, status="failed", error=str(e))

    @staticmethod
    def change_password(request):
        try:
            if not request.user.is_authenticated:
                return CustomJsonResponse(data=None, status="failed", error="Not logged in")
            data = json.loads(request.body)
            old_password = data["old_password"]
            new_password = data["new_password"]
            user = authenticate(request,username=request.user.username,password=old_password,)
            if user is None:
                return CustomJsonResponse(data=None, status="failed", error="Old password is incorrect")
            request.user.set_password(new_password)
            request.user.save()
            return CustomJsonResponse()
        except Exception as e:
            logger.exception("Password change failed")
            return CustomJsonResponse(data=None, status="failed", error=str(e))