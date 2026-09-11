from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Hotel, Room, Reservation, User, OtpCode, Weblog
from .jalali_utils import validate_reservation_window


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ["id", "name", "address", "stars"]


class RoomSerializer(serializers.ModelSerializer):
    price_with_discount = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    hotel = HotelSerializer(read_only=True)

    class Meta:
        model = Room
        fields = [
            "id", "hotel", "name", "description",
            "price_per_night", "has_discount", "discount",
            "price_with_discount", "images",
        ]

    def get_price_with_discount(self, obj):
        if obj.has_discount and obj.discount is not None:
            return obj.price_with_discount()
        return None

    def get_images(self, obj):
        request = self.context.get("request")
        urls = []
        for field in ("image", "image_1", "image_2", "image_3", "image_4"):
            f = getattr(obj, field)
            if f:
                url = f.url
                urls.append(request.build_absolute_uri(url) if request else url)
        return urls


class ReservationSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    total_days = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    reservation_date_start_jalali = serializers.SerializerMethodField()
    reservation_date_end_jalali = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id", "room", "phone_number", "first_name", "last_name",
            "reservation_date_start", "reservation_date_end",
            "reservation_date_start_jalali", "reservation_date_end_jalali",
            "total_days", "total_price", "status", "status_display", "receipt",
        ]

    def get_total_days(self, obj):
        return obj.total_days()

    def get_total_price(self, obj):
        return obj.total_price()

    def get_reservation_date_start_jalali(self, obj):
        return obj.calculate_jalali_start()

    def get_reservation_date_end_jalali(self, obj):
        return obj.calculate_jalali_end()


class ReservationValidateSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=11)
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    reservation_date_start = serializers.CharField()  # 'YYYY/MM/DD' jalali
    reservation_date_end = serializers.CharField()

    def validate(self, attrs):
        room = Room.objects.filter(pk=attrs["room_id"]).first()
        if room is None:
            raise serializers.ValidationError({"room_id": "اتاق پیدا نشد."})
        start_date, end_date = validate_reservation_window(
            room, attrs["reservation_date_start"], attrs["reservation_date_end"]
        )
        attrs["room"] = room
        attrs["_start_date"] = start_date
        attrs["_end_date"] = end_date
        return attrs


class ReservationCreateSerializer(serializers.ModelSerializer):
    reservation_date_start = serializers.CharField(write_only=True)
    reservation_date_end = serializers.CharField(write_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id", "room", "phone_number", "first_name", "last_name",
            "reservation_date_start", "reservation_date_end", "receipt",
        ]
        extra_kwargs = {"receipt": {"required": True}}

    def validate(self, attrs):
        start_date, end_date = validate_reservation_window(
            attrs["room"], attrs["reservation_date_start"], attrs["reservation_date_end"]
        )
        attrs["_start_date"] = start_date
        attrs["_end_date"] = end_date
        return attrs

    def create(self, validated_data):
        validated_data.pop("reservation_date_start")
        validated_data.pop("reservation_date_end")
        start_date = validated_data.pop("_start_date")
        end_date = validated_data.pop("_end_date")
        return Reservation.objects.create(
            reservation_date_start=start_date,
            reservation_date_end=end_date,
            user=self.context["request"].user,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("خطایی در حین ورود به حساب رخ داد")
        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    my_username = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(max_length=11)
    my_email = serializers.EmailField()
    first_name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate_my_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("نام کاربری از قبل وجود دارد")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("شماره تلفن از قبل وجود دارد")
        return value

    def validate_my_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("ایمیل از قبل وجود دارد")
        return value


class VerifyCodeSerializer(serializers.Serializer):
    my_username = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(max_length=11)
    my_email = serializers.EmailField()
    first_name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    code = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "phone_number", "email", "first_name", "last_name"]
        read_only_fields = ["username", "phone_number"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "رمز فعلی صحیح نیست"})
        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "رمزهای وارد شده یکسان نیستند"})
        return attrs


class WeblogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weblog
        fields = ["id", "title", "blog_image", "summary", "body", "pub_date"]


class WeblogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weblog
        fields = ["id", "title", "blog_image", "summary", "pub_date"]