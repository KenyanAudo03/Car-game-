from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("reset-password/", views.reset_password_view, name="reset_password"),
    path("api/save-game-data/", views.save_game_data, name="save_game_data"),
    path("api/sync-on-login/", views.sync_on_login, name="sync_on_login"),
    path("api/check-auth/", views.check_auth, name="check_auth"),
    path("api/reset-game-data/", views.reset_game_data, name="reset_game_data"),
]
