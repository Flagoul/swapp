import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST, require_GET

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status

from users.permissions import IsUserHimself, IsOwner
from users.serializers import *


def register_view(request):
    try:
        username = request.POST["username"]
        password = request.POST["password"]
        password_confirmation = request.POST["password-confirmation"]
        email = request.POST["email"]
    except KeyError:
        return render(request, "users/register.html")

    if password != password_confirmation:
        return render(request, "users/register.html", {
            "error_message": "Passwords don't match."
        })

    try:
        user = User.objects.create_user(username, email, password)
    except IntegrityError:
        return render(request, "users/register.html", {
            "error_message": "User already exists."
        })

    login(request, user)
    return HttpResponseRedirect(reverse("users:account"))


def login_view(request):
    try:
        username = request.POST["username"]
        password = request.POST["password"]
    except KeyError:
        return render(request, "users/login.html")

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("users:account"))
    else:
        return render(request, "users/login.html", {
            "error_message": "Incorrect username/password combination."
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("users:login"))


@login_required(login_url="users:login", redirect_field_name="")
def account_view(request):
    return render(request, "users/account.html", {"username": request.user.username})


@require_GET
@login_required()
def get_personal_account_info(request):
    return JsonResponse({"username": request.user.username})


@require_POST
def api_login(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        username = data["username"]
        password = data["password"]
    except KeyError:
        return JsonResponse({"error": "a value is incorrect"}, status=400)

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse()
    else:
        return JsonResponse({"error": "invalid username/password combination"}, status=401)


@require_GET
@login_required()
def api_logout(request):
    logout(request)
    return HttpResponse()


# FIXME or delete
"""class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(**request.data)
        response = Response(status=status.HTTP_201_CREATED)
        response['Location'] = "/api/users/%d/" % user.id
        return response"""


class UsersAccounts(View):
    def get(self, request):
        # A discuter si besoin ou non d'être connecté si on fait un get sur tous les user a la fois
        if not request.user.is_authenticated():
            return JsonResponse({"error": "you are not connected"}, status=status.HTTP_403_FORBIDDEN)
        # A compléter

        return JsonResponse( status=status.HTTP_200_OK)

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            username = data["username"]
            first_name = data["first_name"]
            last_name = data["last_name"]
            email = data["email"]
            password = data["password"]
        except KeyError:
            return JsonResponse({"error": "a value is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                            password=password)
        except IntegrityError:
            return JsonResponse({"error": "user already exists"}, status=status.HTTP_409_CONFLICT)

        response = HttpResponse()
        response["Location"] = "/api/users/%d/" % user.id
        response.status_code = status.HTTP_201_CREATED
        return response


@require_GET
def user_account(request, pk):
    if not request.user.is_authenticated():
        return JsonResponse({"error": "you are not connected"}, status=status.HTTP_403_FORBIDDEN)
    # A compléter

    return JsonResponse(status=status.HTTP_200_OK)


class UserNameUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserNameSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsUserHimself,)


class UserFirstNameUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserFirstNameSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsUserHimself,)


class UserLastNameUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserLastNameSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsUserHimself,)


class UserEMailUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserEMailSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsUserHimself,)


class UserPasswordUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsUserHimself,)


# Réfléchir à un meilleur moyen de faire l'activation d'un compte.
class UserProfileAccountActiveUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileAccountActiveSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

# Manque categories et +
