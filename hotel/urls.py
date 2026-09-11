from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import api_views

router = DefaultRouter()
router.register(r"rooms", api_views.RoomViewSet, basename="room")
router.register(r"weblogs", api_views.WeblogViewSet, basename="weblog")

app_name = "hotel_api"

urlpatterns = [
    path("weblogs/latest/", api_views.latest_weblogs, name="latest-weblogs"),
    path("rooms/<int:room_id>/reserved-days/", api_views.room_reserved_days, name="reserved-days"),

    path("", include(router.urls)),


    path("reservations/validate/", api_views.ReservationValidateView.as_view(), name="reservation-validate"),
    path("reservations/", api_views.ReservationCreateView.as_view(), name="reservation-create"),
    path("reservations/mine/", api_views.MyReservationsView.as_view(), name="reservation-mine"),

    path("auth/login/", api_views.LoginView.as_view(), name="login"),
    path("auth/logout/", api_views.LogoutView.as_view(), name="logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/register/", api_views.RegisterView.as_view(), name="register"),
    path("auth/verify/", api_views.VerifyCodeView.as_view(), name="verify"),
    path("auth/me/", api_views.MeView.as_view(), name="me"),
    path("auth/change-password/", api_views.ChangePasswordView.as_view(), name="change-password"),
]



# from django.urls import path
# from . import views
# from django.conf.urls.static import static
# from django.conf import settings
#
# app_name = 'hotel'
# urlpatterns = [
#     path('', views.index, name='index'),
#     path('room/<int:room_id>/', views.DetailView.as_view(), name='detail'),
#     path('room/<int:room_id>/reservation/', views.ReservationView.as_view(), name='reservation'),
#     path('room/<int:room_id>/reservation_success/', views.ReservationSuccessView.as_view(), name='reservation_success'),
#     path('status/', views.ReservationStatus.as_view(), name='reservation_status'),
#     path('about/', views.about, name='about'),
#     path("login/", views.UserLoginView.as_view(), name='login'),
#     path("logout/", views.user_logout, name='logout'),
#     path('register/', views.UserRegisterView.as_view(), name='register'),
#     path('verify/', views.UserRegisterVerifyCodeView.as_view(), name='verify_code'),
#     path('update/', views.user_update, name='update'),
#     # path('update_info/', views.update_info, name='update_info'),
#     path('update_password', views.update_password, name='update_password'),
#     path('weblog', views.weblog, name='weblog'),
#     path('weblog/<int:weblog_id>/', views.weblog_detail, name='weblog_detail'),
#     path('checkout/', views.CheckoutView.as_view(), name='checkout'),
# ]
#
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
