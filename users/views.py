from django.contrib.auth import logout, authenticate, login
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from items.models import Category
from items.serializers import InventoryItemSerializer, CategorySerializer, InterestedByCategorySerializer, \
    CreateImageSerializer
from offers.serializers import RetrieveOfferSerializer
from swapp.gmaps_api_utils import get_coordinates, OverQueryLimitError
from users.serializers import *


class OwnUserAccountMixin:
    def get_object(self):
        return self.request.user


@api_view(["GET"])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Returns a CSRF token needed when querying the API."""
    return Response()


@api_view(["POST"])
def login_user(request):
    serializer = LoginUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(**serializer.validated_data)
    if user is not None:
        login(request, user)
        return Response()
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "Invalid username/password combination"})


@api_view(["GET"])
@permission_classes((permissions.IsAuthenticated,))
def logout_user(request):
    """Logs out an user."""
    logout(request)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    if User.objects.filter(username=data["username"]).count() > 0:
        return Response(status=status.HTTP_409_CONFLICT, data="An user with the same username already exists")

    if data["password"] != data["password_confirmation"]:
        raise serializers.ValidationError("Passwords don't match")

    location = {
        "street": data["street"],
        "city": data["city"],
        "region": data["region"],
        "country": data["country"]
    }

    try:
        location_result = get_coordinates(Location(**location))
    except OverQueryLimitError:
        raise ValidationError("The location you specified could not be resolved by our service. Please retry later")

    if len(location_result) == 0:
        raise ValidationError("The location you specified does not exist")

    user = User.objects.create_user(
        username=data["username"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        password=data["password"]
    )

    for k in location.keys():
        setattr(user.location, k, location[k])

    user.location.save()

    c = user.coordinates
    c.latitude = location_result[0]["lat"]
    c.longitude = location_result[0]["lng"]
    c.save()

    response = Response(status=status.HTTP_201_CREATED)
    response["Location"] = "/api/users/%s/" % user.username
    return response


class UserAccount(OwnUserAccountMixin, generics.RetrieveUpdateAPIView):
    """
    Allows to get the current user's account info and update them.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = request.user.userprofile

        return Response({
            "id": user.id,
            "profile_picture_url": None if user.userprofile.image.name == "" else user.userprofile.image.url,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "location": LocationSerializer(user.location).data,
            "last_modification_date": user_profile.last_modification_date,
            "categories": CategorySerializer(user_profile.categories.all(), many=True).data,
            "items": [i.id for i in user.item_set.all()],
            "notes": user.note_set.count(),
            "note_avg": user.userprofile.note_avg,
            "coordinates": CoordinatesSerializer(user.coordinates).data,
            "pending_offers": RetrieveOfferSerializer(
                Offer.objects.filter((Q(item_given__owner=user) | Q(item_received__owner=user)),
                                     Q(answered=False)).order_by("-creation_date"), many=True).data
        })

    def update(self, request, *args, **kwargs):
        new_username = request.data.get("username", None)
        if new_username is not None and User.objects.filter(username=new_username).count() > 0:
            if request.user != User.objects.get(username=new_username):
                return Response(status=status.HTTP_409_CONFLICT,
                                data={"error": "An user with the same username already exists"})
        return super(UserAccount, self).update(request, *args, **kwargs)


@api_view(["PUT"])
@permission_classes((permissions.IsAuthenticated,))
def change_password(request):
    """
    Changes the current user's password.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    old_password = serializer.validated_data["old_password"]
    new_password = serializer.validated_data["new_password"]

    if not request.user.check_password(old_password):
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"old_password": "Wrong password"})

    request.user.set_password(new_password)
    request.user.save()
    return Response(status=status.HTTP_200_OK)


class LocationView(generics.UpdateAPIView):
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user.location

    def perform_update(self, serializer):
        try:
            data = get_coordinates(Location(**serializer.validated_data))
        except OverQueryLimitError:
            raise ValidationError("The location you specified could not be resolved by our service. "
                                   "Please retry later")

        if len(data) == 0:
            raise ValidationError("Could not find any match for the specified location")

        u = self.request.user
        c = u.coordinates
        c.latitude = data[0]["lat"]
        c.longitude = data[0]["lng"]
        c.save()

        serializer.save()


class CategoriesView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = InterestedByCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        userprofile = self.request.user.userprofile
        userprofile.categories.clear()

        for id in serializer.validated_data["interested_by"]:
            userprofile.categories.add(Category.objects.get(pk=id))
            userprofile.save()

        return Response(CategorySerializer(userprofile.categories.all(), many=True).data)


@api_view(["GET"])
def get_public_account_info(request, username):
    """Returns the user's public info."""
    user = get_object_or_404(User, username=username)

    return Response({
        "id": user.id,
        "profile_picture_url": None if user.userprofile.image.name == "" else user.userprofile.image.url,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "location": "%s, %s, %s" % (user.location.city, user.location.region, user.location.country),
        "items": InventoryItemSerializer(user.item_set.all(), many=True).data,
        "notes": user.note_set.count(),
        "note_avg": user.userprofile.note_avg,
        "interested_by": CategorySerializer(user.userprofile.categories, many=True).data,
        "coordinates": CoordinatesSerializer(user.coordinates).data
    })


class NoteViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "update":
            return NoteUpdateSerializer
        return NoteSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        offer = serializer.validated_data["offer"]

        if offer.accepted is not True:
            raise ValidationError("You can't make a note if the offer has not been accepted")
        if offer.item_given.owner == self.request.user:
            serializer.validated_data["user"] = offer.item_received.owner
        elif offer.item_received.owner == self.request.user:
            serializer.validated_data["user"] = offer.item_given.owner
        else:
            raise ValidationError("You are not linked to this offer")

        if Note.objects.filter(offer=offer, user=serializer.validated_data["user"]).count() > 0:
            raise ValidationError("You have already noted this offer")
        serializer.save()


@api_view(["POST"])
@permission_classes((permissions.IsAuthenticated,))
def set_profile_image(request):
    serializer = CreateImageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    userprofile = request.user.userprofile
    userprofile.image = serializer.validated_data["image"]
    userprofile.save()

    return Response(status=status.HTTP_201_CREATED, headers={"Location": userprofile.image.url})
