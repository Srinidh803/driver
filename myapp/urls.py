from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("start/", views.start_journey, name="start_journey"),
    path("share/<int:journey_id>/", views.share_location, name="share_location"),
    path("track/<int:journey_id>/", views.track_bus, name="track_bus"),
    path("api/location/<int:journey_id>/", views.latest_location, name="latest_location"),
]
