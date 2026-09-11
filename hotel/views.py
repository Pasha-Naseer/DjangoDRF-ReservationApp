import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Reservation
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import ChangePasswordForm
from django.views import View
from .forms import UserRegistrationForm, VerifyCodeForm,  UserChangeFormUser, UserLoginForm, ReservationForm
from utils import send_otp_code
from .models import OtpCode, User, Weblog
from datetime import datetime, date, time, timedelta
from django.utils import timezone
# was
# from khayyam import JalaliDate, JalaliDatetime, TehranTimezone
# is
import jdatetime
import json


def index(request):
    room_list = Room.objects.all()
    weblogs = Weblog.objects.order_by("-pub_date")[:3]
    context = {"room_list": room_list,
               'weblogs': weblogs}
    return render(request, 'hotel/index.html', context)


class ReservationStatus(View):
    def get(self, request):
        if request.user.is_authenticated:
            reservations = Reservation.objects.filter(user=request.user)
            context = {'reservations': reservations}
            return render(request, 'hotel/reservation_status.html', context)
        messages.error(request, 'ابتدا وارد حساب کاربری شوید')
        return redirect('hotel:login')


class DetailView(View):
    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        context = {
            'room': room,
        }
        return render(request, 'hotel/detail.html', context)


class ReservationView(View):
    form = ReservationForm

    def get(self, request, room_id):
        if request.user.is_authenticated:
            room = get_object_or_404(Room, pk=room_id)

            #reservations = room.reservation_set.filter(room=room)
            # reservation_times = []
            #
            # for i in reservations:
            #     item = []
            #     item.append(i.reservation_date_start)
            #     item.append(i.reservation_date_end)
            #     reservation_times.append(item)
            # jalali_leap_years = [
            #     1404, 1408, 1412, 1416, 1420, 1424, 1428, 1432, 1436, 1440,
            #     1444, 1448, 1452, 1456, 1460, 1464, 1468, 1472, 1476, 1480,
            #     1484, 1488, 1492
            # ]
            # months_31 = range(1, 7)
            # months_30 = range(7, 13)
            # print(reservation_times)
            # all_reserved_dates = []
            # for j in range(len(reservation_times)):
            #     # was
            #     # start_jalali = JalaliDatetime(reservation_times[j][0])
            #     # end_jalali = JalaliDatetime(reservation_times[j][1])
            #     # is
            #     start_jalali = jdatetime.date.fromgregorian(date=reservation_times[j][0])
            #     end_jalali = jdatetime.date.fromgregorian(date=reservation_times[j][1])
            #
            #     print(start_jalali, reservation_times[j][0])
            #     print(end_jalali, reservation_times[j][1])
            #
            #     if start_jalali.year == end_jalali.year:
            #         if start_jalali.month == end_jalali.month:
            #             reserve_range = range(int(start_jalali.day), int(end_jalali.day))
            #             for r in reserve_range:
            #                 all_reserved_dates.append([start_jalali.year, start_jalali.month, r])
            #         elif start_jalali.month + 1 == end_jalali.month:
            #             if start_jalali.month in months_30:
            #                 reserve_range1 = range(start_jalali.day, 31)
            #                 reserve_range2 = range(1, end_jalali)
            #                 for r in reserve_range1:
            #                     all_reserved_dates.append([start_jalali.year, start_jalali.month, r])
            #                 for r in reserve_range2:
            #                     all_reserved_dates.append([start_jalali.year, end_jalali.month, r])
            #             elif start_jalali.month in months_31:
            #                 reserve_range1 = range(start_jalali.day, 32)
            #                 reserve_range2 = range(1, end_jalali)
            #                 for r in reserve_range1:
            #                     all_reserved_dates.append([start_jalali.year, start_jalali.month, r])
            #                 for r in reserve_range2:
            #                     all_reserved_dates.append([start_jalali.year, end_jalali.month, r])
            #     elif start_jalali.year + 1 == end_jalali.year:
            #         if start_jalali.year in jalali_leap_years:
            #             if start_jalali.month == 12 and end_jalali.month == 1:
            #                 reserve_range1 = range(start_jalali.day, 31)
            #                 reserve_range2 = range(1, end_jalali)
            #                 for r in reserve_range1:
            #                     all_reserved_dates.append([start_jalali.year, start_jalali.month, r])
            #                 for r in reserve_range2:
            #                     all_reserved_dates.append([end_jalali.year, end_jalali.month, r])
            #         else:
            #             if start_jalali.month == 12 and end_jalali.month == 1:
            #                 reserve_range1 = range(start_jalali.day, 30)
            #                 reserve_range2 = range(1, end_jalali)
            #                 for r in reserve_range1:
            #                     all_reserved_dates.append([start_jalali.year, start_jalali.month, r])
            #                 for r in reserve_range2:
            #                     all_reserved_dates.append([end_jalali.year, end_jalali.month, r])

            reservations = Reservation.objects.filter(room_id=room_id)
            reserved_days = []

            for r in reservations:
                start = jdatetime.date.fromgregorian(date=r.reservation_date_start)
                end = jdatetime.date.fromgregorian(date=r.reservation_date_end)
                # print([start, end])
                current = start
                while current < end:
                    reserved_days.append(current.strftime("%Y/%m/%d"))
                    current += timedelta(days=1)
            # print(reserved_days)
            context = {"form": self.form,
                       'room': room,
                       "reserved_days": json.dumps(reserved_days),
                       #'all_reserved_dates': all_reserved_dates,

            }

            return render(request, 'hotel/reservation.html', context)
        else:
            messages.error(request, 'برای رزرو اتاق باید وارد حساب کاربری شوید')
            return redirect('hotel:login')

    def post(self, request, room_id):
        if request.user.is_authenticated:
            form = self.form(request.POST)
            if form.is_valid():
                room = get_object_or_404(Room, pk=room_id)
                phone_number = form.cleaned_data['phone_number']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                reservation_date_start = form.cleaned_data['reservation_date_start']
                reservation_date_end = form.cleaned_data['reservation_date_end']
                # print(str(reservation_date_start))
                # print(str(reservation_date_end))
                if len(reservation_date_start) != 10 or reservation_date_start[4] != "/" or reservation_date_start[7] != "/":
                    messages.error(request, "فرمت وارد شده صحیح نمی باشد!")
                    return redirect('hotel:reservation', room_id)
                # ex) 1404/02/03
                start_year = reservation_date_start[:4]
                start_month = reservation_date_start[5:7]
                if start_month[0] == 0:
                    start_month = start_month[1]
                start_day = reservation_date_start[8:]
                if start_day[0] == 0:
                    start_day = start_day[1]
                # was
                # reservation_date_start = JalaliDate(start_year, start_month, start_day).todate()
                # is

                reservation_date_start = jdatetime.date(int(start_year), int(start_month), int(start_day)).togregorian()


                if len(reservation_date_end) != 10 or reservation_date_end[4] != "/" or reservation_date_end[7] != "/":
                    messages.error(request, "فرمت وارد شده صحیح نمی باشد!")
                    return redirect('hotel:reservation', room_id)
                # ex) 1404/02/03
                end_year = reservation_date_end[:4]
                end_month = reservation_date_end[5:7]
                if end_month[0] == 0:
                    end_month = end_month[1]
                end_day = reservation_date_end[8:]
                if end_day[0] == 0:
                    end_day = end_day[1]
                # was
                # reservation_date_end = JalaliDate(end_year, end_month, end_day).todate()
                # is
                reservation_date_end = jdatetime.date(int(end_year), int(end_month), int(end_day)).togregorian()


                # --- NEW VALIDATION: no more than 2 months earlier or later ---
                today = date.today()
                two_months_before = today - timedelta(days=60)
                two_months_after = today + timedelta(days=60)

                if not (two_months_before <= reservation_date_start <= two_months_after):
                    messages.error(request, "تاریخ شروع رزرو باید حداکثر تا دو ماه بعد از امروز باشد.")
                    return redirect('hotel:reservation', room_id)

                if not (two_months_before <= reservation_date_end <= two_months_after):
                    messages.error(request, "تاریخ پایان رزرو باید حداکثر تا دو ماه بعد از امروز باشد.")
                    return redirect('hotel:reservation', room_id)

                if not today < reservation_date_start or not today < reservation_date_end or not reservation_date_end > reservation_date_start:
                    messages.error(request, "لظفا تاریخ را بررسی کنید و دوباره اقدام به رزرو نمایید.")
                    return redirect("hotel:reservation", room.id)

                year_scale = int(end_year) - int(start_year)
                if end_year == start_year:
                    month_scale = int(end_month) - int(start_month)
                    # print(end_month)
                    # print(start_month)
                    # print(int(end_month) - int(start_month))
                    if month_scale != 0 and month_scale != 1:
                        messages.error(request,"بازه زمانی انتخاب شده از حد قابل قبول بزرگتر است")
                        return redirect("hotel:reservation", room.id)

                elif year_scale == 1:
                    if int(start_month) == 12 and int(end_month) == 1:
                        pass
                    else:
                        messages.error(request, "بازه زمانی انتخاب شده از حد قابل قبول بزرگتر است")
                        return redirect("hotel:reservation", room.id)
                else:
                    messages.error(request, "بازه زمانی انتخاب شده از حد قابل قبول بزرگتر است")
                    return redirect("hotel:reservation", room.id)

                if reservation_date_start and reservation_date_end:
                    overlap = Reservation.objects.filter(
                        room=room,
                        reservation_date_start__lt=reservation_date_end,
                        reservation_date_end__gt=reservation_date_start,
                    ).exists()
                    if overlap:
                        messages.error(request, "نداخل بازه زمانی!")
                        return redirect('hotel:reservation', room_id)

                request.session['pending_reservation'] = {
                    "room_id": room.id,
                    "phone_number": phone_number,
                    "first_name": first_name,
                    "last_name": last_name,
                    "reservation_date_start": reservation_date_start.isoformat(),
                    "reservation_date_end": reservation_date_end.isoformat(),
                }

                return redirect('hotel:checkout')

            messages.error(request, 'خطایی در فرایند ثبت رزرو ایجاد شد')
            return redirect('hotel:reservation', room_id)

        else:
            messages.error(request, 'برای رزرو اتاق باید وارد حساب کاربری شوید')
            return redirect('hotel:login')


class ReservationSuccessView(View):
    def get(self, request, room_id):
        return render(request, 'hotel/reservation_success.html', {})


# def update_info(request):
#     if request.user.is_authenticated:
#         current_user = Profile.objects.get(user__id=request.user.id)
#         form = UserInfoForm(request.POST or None, instance=current_user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'اطلاعات کاربری آپدیت شد')
#             return redirect("hotel:index")
#         return render(request, 'hotel/update_info.html', {'form': form, })
#     else:
#         messages.error(request, 'برای دسترسی به این پیج باید وارد حساب شوید!')
#         return redirect('hotel:login')


def about(request):
    return render(request, 'hotel/about.html', {})


class UserLoginView(View):
    form = UserLoginForm
    def get(self, request):
        if request.user.is_authenticated:
            messages.error(request, 'شما قبلا وارد حساب شده اید.')
            return redirect('hotel:index')
        form = self.form
        return render(request, 'hotel/login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "شما با موفقیت به حساب وارد شدید")
                return redirect("hotel:index")
            else:
                messages.error(request, "خطایی در حین ورود به حساب رخ داد")
                return redirect('hotel:login')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "شما با موفقیت از حساب خارج شدید")
        return redirect("hotel:login")
    else:
        messages.error(request, "برای خروج از حساب باید وارد آن شده باشید.")
        return redirect('hotel:login')


class UserRegisterView(View):
    form_class = UserRegistrationForm

    def get(self, request):
        form = self.form_class
        return render(request,'hotel/register.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            while OtpCode.objects.filter(phone_number=form.cleaned_data['phone_number']).exists():
                OtpCode.objects.get(phone_number=form.cleaned_data['phone_number']).delete()
            random_code = random.randint(1000, 9999)

            send_otp_code(form.cleaned_data['phone_number'], random_code)

            OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=random_code)
            request.session['user_registration_info'] = {
                'username': form.cleaned_data['my_username'],
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['my_email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password': form.cleaned_data['password'],
            }
            messages.success(request, 'کدی برای شما ارسال شد', 'success')
            return redirect('hotel:verify_code')
        messages.success(request,"فرم خود را بازبینی کنید", 'success')
        return redirect('hotel:register')


# is
class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, 'hotel/verify.html', {'form': form})

    def post(self, request):
        scale = time(0, 3, 0, 0)
        duration = timedelta(hours=scale.hour, minutes=scale.minute, seconds=scale.second,
                             microseconds=scale.microsecond)
        for i in OtpCode.objects.all():
            if i.created + duration < timezone.now():
                i.delete()
        user_session = request.session['user_registration_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            if not code_instance.calculate_date() == datetime.now().date():
                messages.error(request, 'کد منقضی شد!', 'danger')
                return redirect('hotel:register')
            substraction = datetime.combine(date.today(), datetime.now().time()) - datetime.combine(date.today(), code_instance.calculate_time())

            #print(datetime.now().time())
            #print(code_instance.calculate_time())
            #print(substraction)
            #print(duration)
            if substraction > duration:
                messages.error(request, 'کد منقضی شد!', 'danger')
                return redirect('hotel:register')
            if User.objects.filter(username=user_session['username']).exists():
                messages.error(request, 'نام کاربری از قبل وجود دارد')
                return redirect('hotel:register')
            if User.objects.filter(phone_number=user_session['phone_number']).exists():
                messages.error(request, 'شماره تلفن از قبل وجود دارد')
                return redirect('hotel:register')
            if User.objects.filter(email=user_session['email']).exists():
                messages.error(request, 'ایمیل از قبل وجود دارد')
                return redirect('hotel:register')
            cd = form.cleaned_data
            if cd['code'] == code_instance.code:
                User.objects.create_user(user_session['username'], user_session['phone_number'],
                                         user_session['email'], user_session['first_name'], user_session['last_name'],
                                         user_session['password'],)
                code_instance.delete()
                messages.success(request, 'کاربر با موفقیت ثبت شد', 'success')
                return redirect('hotel:login')
            else:
                messages.error(request, "کد اشتباه!", 'danger')
                return redirect('hotel:verify_code')
        return render(request, 'hotel/register.html', {'form': form})


def user_update(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UserChangeFormUser(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, 'کاربر آپدیت شد')
            return redirect("hotel:update")
        return render(request, 'hotel/update_user.html', {'user_form': user_form})
    else:
        messages.error(request, 'برای ورود به پیج باید وارد حساب شوید!')
        return redirect('hotel:index')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill the form?
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, 'رمز شما آپدیت شد!')
                return redirect('hotel:login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('hotel:update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'hotel/update_password.html', {'form': form})
    else:
        messages.error(request, 'برای ورود به پیج باید وارد حساب شوید!')
        return redirect('hotel:index')

def weblog(request):
    weblogs = Weblog.objects.all()
    context = {"weblogs": weblogs}
    return render(request, 'hotel/weblog.html', context)
    

def weblog_detail(request, weblog_id):
    weblog = get_object_or_404(Weblog, pk=weblog_id)
    context = {
        'weblog': weblog,
    }
    return render(request, 'hotel/weblog_detail.html', context)


class CheckoutView(View):

    def get(self, request):
        # if 'pending_reservation' not in request.session:
        #     messages.error(request, "رزروی برای پرداخت وجود ندارد.")
        #     return redirect('hotel:index')
        #
        # return render(request, 'hotel/checkout.html')

        if 'pending_reservation' not in request.session:
            messages.error(request, "رزروی برای پرداخت وجود ندارد.")
            return redirect('hotel:index')

        data = request.session['pending_reservation']

        room = Room.objects.get(id=data['room_id'])


        start = date.fromisoformat(data['reservation_date_start'])
        end = date.fromisoformat(data['reservation_date_end'])


        reservation = Reservation(
            room=room,
            reservation_date_start=start,
            reservation_date_end=end
        )

        context = {
            "reservation": reservation
        }

        return render(request, 'hotel/checkout.html', context)

    def post(self, request):
        if 'pending_reservation' not in request.session:
            messages.error(request, "رزروی برای پرداخت وجود ندارد.")
            return redirect('hotel:index')

        receipt = request.FILES.get('receipt')

        if not receipt:
            messages.error(request, "لطفاً تصویر رسید را بارگذاری کنید.")
            return redirect('hotel:checkout')

        data = request.session['pending_reservation']

        room = Room.objects.get(id=data['room_id'])

        reservation = Reservation.objects.create(
            room=room,
            phone_number=data['phone_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            reservation_date_start=date.fromisoformat(data['reservation_date_start']),
            reservation_date_end=date.fromisoformat(data['reservation_date_end']),
            user=request.user,
            receipt=receipt  # <-- you must add this field
        )

        # Clear session
        del request.session['pending_reservation']

        return render(request, 'hotel/reservation_success.html')