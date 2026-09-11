from django.contrib import admin
from .models import Reservation, Hotel, Room, User, OtpCode, Weblog
from .forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
# was
# from khayyam import JalaliDatetime
# is
import jdatetime

admin.site.register(Weblog)
admin.site.register(Hotel)
admin.site.register(Room)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'room',
        'user',
        'phone_number',
        'first_name',
        'last_name',
        'reservation_date_start',
        'reservation_date_end',
        'status',
        'calculate_jalali',
    )

    readonly_fields = ('calculate_jalali',)
    def calculate_jalali(self, obj):
        # was
        # start_jalali = JalaliDatetime(obj.reservation_date_start).strftime('%Y/%m/%d')
        # end_jalali = JalaliDatetime(obj.reservation_date_end).strftime('%Y/%m/%d')
        # is
        start_jalali = jdatetime.date.fromgregorian(date=obj.reservation_date_start).strftime('%Y/%m/%d')
        end_jalali = jdatetime.date.fromgregorian(date=obj.reservation_date_end).strftime('%Y/%m/%d')
        return f"{start_jalali} -- {end_jalali}"
    calculate_jalali.short_description = "Reservation (Jalali)"


# class ProfileInline(admin.StackedInline):
#     model = Profile


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    model = User
    # inlines = [ProfileInline]
    list_display = ("username", 'phone_number', 'first_name', 'last_name', 'email')
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('username', 'phone_number', 'email', 'first_name', 'last_name', 'password')}),
        ('permissions', {'fields': ('is_admin', 'last_login')})
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'phone_number', 'email', 'first_name', 'last_name', 'password1', 'password2')}),
    )

    search_fields = ('username', 'phone_number')
    ordering = ("username",)
    filter_horizontal = ()


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created')