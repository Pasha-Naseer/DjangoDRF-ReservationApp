from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from django.utils import timezone
from django.db.models.signals import post_save
# was
# from khayyam import JalaliDatetime
# is
import jdatetime


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    stars = models.IntegerField(default=3)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    image = models.ImageField(blank=True, default="fallback.jpg")
    image_1 = models.ImageField(blank=True, default="fallback.jpg")
    image_2 = models.ImageField(blank=True, default="fallback.jpg")
    image_3 = models.ImageField(blank=True, default="fallback.jpg")
    image_4 = models.ImageField(blank=True, default="fallback.jpg")
    description = models.TextField()
    price_per_night = models.DecimalField(default=0, decimal_places=0, max_digits=10)
    has_discount = models.BooleanField(default=False)
    discount = models.DecimalField(null=True, blank=True, decimal_places=0, max_digits=2)

    def price_with_discount(self):
        amount = self.price_per_night - self.price_per_night * self.discount / 100
        return amount

    def __str__(self):
        return self.name


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('A', 'Accepted'),
        ('P', 'Pending'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    reservation_date_start = models.DateField()
    reservation_date_end = models.DateField()
    receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', null=True)

    def total_days(self):
        jalali_leap_years = [
            1404, 1408, 1412, 1416, 1420, 1424, 1428, 1432, 1436, 1440,
            1444, 1448, 1452, 1456, 1460, 1464, 1468, 1472, 1476, 1480,
            1484, 1488, 1492
        ]
        months_31 = range(1, 7)
        months_30 = range(7, 13)

        # was
        # start_jalali = JalaliDatetime(self.reservation_date_start)
        # end_jalali = JalaliDatetime(self.reservation_date_end)
        # is
        start_jalali = jdatetime.date.fromgregorian(date=self.reservation_date_start)
        end_jalali = jdatetime.date.fromgregorian(date=self.reservation_date_end)

        if start_jalali.year == end_jalali.year:
            if start_jalali.month == end_jalali.month:
                total = end_jalali.day - start_jalali.day
                return total
            elif start_jalali.month + 1 == end_jalali.month:
                if start_jalali.month in months_30:
                    total = 30 - start_jalali.day + end_jalali.day
                    return total
                elif start_jalali.month in months_31:
                    total = 31 - start_jalali.day + end_jalali.day
                    return total
                else:
                    return None
            else:
                return None
        elif start_jalali.year + 1 == end_jalali.year:
            if start_jalali.year in jalali_leap_years:
                if start_jalali.month == 12 and end_jalali.month == 1:
                    total = 30 - start_jalali.month + 1
                    return total
                else:
                    return None
            else:
                if start_jalali.month == 12 and end_jalali.month == 1:
                    total = 29 - start_jalali.month + 1
                    return total
                else:
                    return None

        #     total = self.reservation_date_end - self.reservation_date_start
        #     return total
        # else:
        #     if self.reservation_date_start.year != self.reservation_date_end.year:
        #         if self.reservation_date_start.year in jalali_leap_years:
        #             total = 30 - self.reservation_date_start.day + self.reservation_date_end.day
        #             return total
        #         else:
        #             total = 29 - self.reservation_date_start.day + self.reservation_date_end.day
        #     elif self.reservation_date_end

    def total_price(self):
        # return self.room.price_per_night * self.total_days()
        if self.room.has_discount:
            return self.room.price_with_discount() * self.total_days()
        return self.price_per_night * self.total_days()

    def calculate_jalali_start(self):
        start_jalali = jdatetime.date.fromgregorian(date=self.reservation_date_start).strftime('%Y/%m/%d')
        return start_jalali

    def calculate_jalali_end(self):
        end_jalali = jdatetime.date.fromgregorian(date=self.reservation_date_end).strftime('%Y/%m/%d')
        return end_jalali

    def __str__(self):
        return f"{self.user} - {self.room}"


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=225, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    # required fields? for superuser?
    REQUIRED_FIELDS = ['phone_number', 'email', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class OtpCode(models.Model):
    phone_number = models.CharField(max_length=12)
    code = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phone_number} - {self.code} - {self.created.time()} - {timezone.localtime(self.created).date()}'

    def calculate_time(self):
        create_time = timezone.localtime(self.created).time()
        return create_time

    def calculate_date(self):
        create_date = timezone.localtime(self.created).date()
        return create_date

class Weblog(models.Model):
    title = models.CharField(max_length=200)
    blog_image = models.ImageField(default="fallback.png")
    summary = models.TextField(max_length=150)
    body = models.TextField()
    pub_date = models.DateTimeField("date published", null=True)

    def __str__(self):
        return self.title


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     date_modified = models.DateTimeField(User, auto_now=True)
#     # Used2B
#     # phone = models.CharField(max_length=15, blank=True)
#     address1 = models.CharField(max_length=200, blank=True)
#     address2 = models.CharField(max_length=200, blank=True)
#     city = models.CharField(max_length=200, blank=True)
#     state = models.CharField(max_length=200, blank=True)
#     zipcode = models.CharField(max_length=200, blank=True)
#     # phase2) country = models.CharField(max_length=200, blank=True)
#     old_cart = models.CharField(max_length=200, blank=True)

#     def __str__(self):
#         return self.user.username


# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         user_profile = Profile(user=instance)
#         user_profile.save()


# post_save.connect(create_profile, sender=User)



