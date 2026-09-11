from datetime import date, timedelta

import jdatetime
from rest_framework import serializers


def parse_jalali_string(value, field_name="date"):
    if not value or len(value) != 10 or value[4] != "/" or value[7] != "/":
        raise serializers.ValidationError({field_name: "فرمت وارد شده صحیح نمی باشد!"})

    year_s, month_s, day_s = value[:4], value[5:7], value[8:]
    try:
        year, month, day = int(year_s), int(month_s), int(day_s)
        return jdatetime.date(year, month, day).togregorian(), year_s, month_s
    except ValueError:
        raise serializers.ValidationError({field_name: "فرمت وارد شده صحیح نمی باشد!"})


def validate_reservation_window(room, start_str, end_str):
    from .models import Reservation  # local import to avoid circulars

    start_date, start_year, start_month = parse_jalali_string(start_str, "reservation_date_start")
    end_date, end_year, end_month = parse_jalali_string(end_str, "reservation_date_end")

    today = date.today()
    two_months_before = today - timedelta(days=60)
    two_months_after = today + timedelta(days=60)

    if not (two_months_before <= start_date <= two_months_after):
        raise serializers.ValidationError(
            {"reservation_date_start": "تاریخ شروع رزرو باید حداکثر تا دو ماه بعد از امروز باشد."}
        )
    if not (two_months_before <= end_date <= two_months_after):
        raise serializers.ValidationError(
            {"reservation_date_end": "تاریخ پایان رزرو باید حداکثر تا دو ماه بعد از امروز باشد."}
        )
    if not (today < start_date and today < end_date and end_date > start_date):
        raise serializers.ValidationError("لطفا تاریخ را بررسی کنید و دوباره اقدام به رزرو نمایید.")

    year_scale = int(end_year) - int(start_year)
    if year_scale == 0:
        month_scale = int(end_month) - int(start_month)
        if month_scale not in (0, 1):
            raise serializers.ValidationError("بازه زمانی انتخاب شده از حد قابل قبول بزرگتر است")
    elif year_scale == 1:
        if not (int(start_month) == 12 and int(end_month) == 1):
            raise serializers.ValidationError("بازه زمانی انتخاب شده از حد قابل قبول بزرگتر است")
    else:
        raise serializers.ValidationError("بازه زمانی انتخاب شده از حد قابل قبول بزرگتر است")

    overlap = Reservation.objects.filter(
        room=room,
        reservation_date_start__lt=end_date,
        reservation_date_end__gt=start_date,
    ).exists()
    if overlap:
        raise serializers.ValidationError("این بازه زمانی قبلاً رزرو شده است.")

    return start_date, end_date


def reserved_days_for_room(room_id):
    from .models import Reservation

    reservations = Reservation.objects.filter(room_id=room_id)
    reserved_days = []
    for r in reservations:
        start = jdatetime.date.fromgregorian(date=r.reservation_date_start)
        end = jdatetime.date.fromgregorian(date=r.reservation_date_end)
        current = start
        while current < end:
            reserved_days.append(current.strftime("%Y/%m/%d"))
            current += timedelta(days=1)
    return reserved_days