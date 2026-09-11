import random
from datetime import time, timedelta, datetime

from django.utils import timezone
from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import send_otp_code
from .models import Room, Reservation, OtpCode, User, Weblog
from .jalali_utils import reserved_days_for_room
from .serializers import (
    RoomSerializer, ReservationSerializer, ReservationValidateSerializer,
    ReservationCreateSerializer, LoginSerializer, RegisterSerializer,
    VerifyCodeSerializer, UserSerializer, ChangePasswordSerializer,
    WeblogSerializer, WeblogListSerializer,
)
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
OTP_LIFETIME = timedelta(hours=0, minutes=3, seconds=0)


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh),
            "access": str(refresh.access_token)}


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]


class WeblogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Weblog.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return WeblogSerializer if self.action == "retrieve" else WeblogListSerializer


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def latest_weblogs(request):
    weblogs = Weblog.objects.order_by("-pub_date")[:6]
    return Response(WeblogListSerializer(weblogs, many=True, context={"request": request}).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def room_reserved_days(request, room_id):
    return Response({"reserved_days": reserved_days_for_room(room_id)})


class ReservationValidateView(APIView):
    """POST /api/reservations/validate/ — same checks as the old
    ReservationView.post(), minus actually saving anything."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReservationValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data
        return Response({
            "room_id": v["room"].id,
            "phone_number": v["phone_number"],
            "first_name": v["first_name"],
            "last_name": v["last_name"],
            "reservation_date_start": v["reservation_date_start"],
            "reservation_date_end": v["reservation_date_end"],
        })


class ReservationCreateView(generics.CreateAPIView):
    """POST /api/reservations/ (multipart, receipt file required) — replaces
    CheckoutView.post(). Re-validates everything server-side."""
    serializer_class = ReservationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class MyReservationsView(generics.ListAPIView):
    """GET /api/reservations/mine/ — replaces ReservationStatus."""
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response({"user": UserSerializer(user).data, **_tokens_for(user)})


class LogoutView(APIView):
    """POST /api/auth/logout/ { refresh } — blacklists the refresh token.
    Requires SIMPLE_JWT token blacklisting: add 'rest_framework_simplejwt.token_blacklist'
    to INSTALLED_APPS and run migrate."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh")).blacklist()
        except (TokenError, AttributeError):
            pass  # already invalid/expired — logging out is still a success from the client's POV
        return Response({"detail": "شما با موفقیت از حساب خارج شدید"})


class RegisterView(APIView):
    """POST /api/auth/register/ — sends OTP, does not create the user yet."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        OtpCode.objects.filter(phone_number=phone_number).delete()
        random_code = random.randint(1000, 9999)
        send_otp_code(phone_number, random_code)
        OtpCode.objects.create(phone_number=phone_number, code=random_code)

        return Response({"detail": "کدی برای شما ارسال شد"}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    """POST /api/auth/verify/ — checks the OTP and, if valid, creates the
    user and logs them in (returns JWT pair), same expiry rules as before."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # sweep expired codes, same as before
        for otp in OtpCode.objects.all():
            if otp.created + OTP_LIFETIME < timezone.now():
                otp.delete()

        code_instance = OtpCode.objects.filter(phone_number=data["phone_number"]).first()
        if code_instance is None:
            return Response({"detail": "کد منقضی شد!"}, status=status.HTTP_400_BAD_REQUEST)

        if code_instance.calculate_date() != datetime.now().date():
            return Response({"detail": "کد منقضی شد!"}, status=status.HTTP_400_BAD_REQUEST)

        elapsed = datetime.combine(datetime.now().date(), datetime.now().time()) - \
            datetime.combine(datetime.now().date(), code_instance.calculate_time())
        if elapsed > OTP_LIFETIME:
            return Response({"detail": "کد منقضی شد!"}, status=status.HTTP_400_BAD_REQUEST)

        if code_instance.code != data["code"]:
            return Response({"detail": "کد اشتباه!"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=data["my_username"]).exists():
            return Response({"detail": "نام کاربری از قبل وجود دارد"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(phone_number=data["phone_number"]).exists():
            return Response({"detail": "شماره تلفن از قبل وجود دارد"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=data["my_email"]).exists():
            return Response({"detail": "ایمیل از قبل وجود دارد"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            data["my_username"], data["phone_number"], data["my_email"],
            data["first_name"], data["last_name"], data["password"],
        )
        code_instance.delete()
        return Response({"user": UserSerializer(user).data, **_tokens_for(user)}, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password1"])
        request.user.save()
        return Response({"detail": "رمز شما آپدیت شد!"})