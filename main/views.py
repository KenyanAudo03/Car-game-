from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .models import GameProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
from django.contrib.auth.decorators import login_required


# Create your views here.
def homepage(request):
    return render(request, "main/homepage.html")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken.")
                return render(request, "main/register.html", {"form": form})
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("homepage")  # redirect to your game/homepage
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("homepage")  # or your game page view name
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "main/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("homepage")


def reset_password_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password updated. You can now log in.")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Username not found.")

    return render(request, "main/reset_password.html")


@login_required
@require_http_methods(["POST"])
def save_game_data(request):
    """Save game data for authenticated users"""
    try:
        data = json.loads(request.body)

        # Get or create user profile
        profile, created = GameProfile.objects.get_or_create(
            user=request.user,
            defaults={"high_score": 0, "high_level": 1, "music_enabled": True},
        )

        # Update profile with new data
        profile.high_score = max(profile.high_score, data.get("highScore", 0))
        profile.high_level = max(profile.high_level, data.get("highLevel", 1))
        profile.music_enabled = data.get("musicEnabled", True)
        profile.save()

        return JsonResponse(
            {"success": True, "message": "Game data saved successfully"}
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def sync_on_login(request):
    """Synchronize local browser data with user account on login"""
    try:
        data = json.loads(request.body)

        # Get or create user profile
        profile, created = GameProfile.objects.get_or_create(
            user=request.user,
            defaults={"high_score": 0, "high_level": 1, "music_enabled": True},
        )

        # Merge local data with server data (take the maximum values)
        local_high_score = data.get("highScore", 0)
        local_high_level = data.get("highLevel", 1)
        local_music_enabled = data.get("musicEnabled", True)

        # Update profile with merged data
        profile.high_score = max(profile.high_score, local_high_score)
        profile.high_level = max(profile.high_level, local_high_level)
        profile.music_enabled = local_music_enabled  # Use local preference
        profile.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Data synchronized successfully",
                "data": {
                    "high_score": profile.high_score,
                    "high_level": profile.high_level,
                    "music_enabled": profile.music_enabled,
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def check_auth(request):
    """Check if user is authenticated"""
    return JsonResponse(
        {
            "authenticated": request.user.is_authenticated,
            "user_id": request.user.id if request.user.is_authenticated else None,
        }
    )


@login_required
@require_http_methods(["POST"])
def reset_game_data(request):
    """Reset game data for authenticated users"""
    try:
        # Get or create user profile
        profile, created = GameProfile.objects.get_or_create(
            user=request.user,
            defaults={"high_score": 0, "high_level": 1, "music_enabled": True},
        )

        # Reset profile data
        profile.high_score = 0
        profile.high_level = 1
        profile.save()

        return JsonResponse(
            {"success": True, "message": "Game data reset successfully"}
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
