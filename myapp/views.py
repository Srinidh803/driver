from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser, Journey, BusLocation
import json

# -------------------------
# REGISTER VIEW
# -------------------------
def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_conductor = request.POST.get("is_conductor") == "on"

        if CustomUser.objects.filter(name=name).exists():
            messages.error(request, "Username already taken.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            hashed_pw = make_password(password)
            CustomUser.objects.create(
                name=name,
                email=email,
                password=hashed_pw,
                is_conductor=is_conductor
            )
            messages.success(request, "Registration successful. Please login.")
            return redirect("login")

    return render(request, "register.html")


# -------------------------
# LOGIN VIEW
# -------------------------
def login_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(name=name)
            if check_password(password, user.password):
                # Save user ID in session
                request.session["user_id"] = user.id
                messages.success(request, f"Welcome back, {user.name}!")
                return redirect("home")
            else:
                messages.error(request, "Invalid password.")
        except CustomUser.DoesNotExist:
            messages.error(request, "No such user.")

    return render(request, "login.html")


# -------------------------
# LOGOUT VIEW
# -------------------------
def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect("login")


# -------------------------
# HOME VIEW
# -------------------------
def home(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = CustomUser.objects.get(id=user_id)
    return render(request, "home.html", {"user": user})


# -------------------------
# START JOURNEY (Conductor only)
# -------------------------
def start_journey(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = CustomUser.objects.get(id=user_id)

    if not user.is_conductor:
        messages.error(request, "Only conductors can start journeys.")
        return redirect("home")

    if request.method == "POST":
        start = request.POST.get("start")
        end = request.POST.get("end")
        stops = request.POST.get("stops")

        journey = Journey.objects.create(
            conductor=user,
            start_location=start,
            end_location=end,
            stop_points=stops
        )
        messages.success(request, "Journey started!")
        return redirect("share_location", journey.id)

    return render(request, "start_journey.html")


# -------------------------
# SHARE LOCATION (Conductor only)
# -------------------------
def share_location(request, journey_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Login required"}, status=403)
    user = CustomUser.objects.get(id=user_id)

    if not user.is_conductor:
        return JsonResponse({"error": "Not authorized"}, status=403)

    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        lat = data.get("latitude")
        lon = data.get("longitude")

        journey = Journey.objects.get(id=journey_id, conductor=user)
        BusLocation.objects.create(journey=journey, latitude=lat, longitude=lon)

        return JsonResponse({"status": "location saved"})

    return render(request, "share_location.html", {"journey_id": journey_id})


# -------------------------
# TRACK BUS (Passenger)
# -------------------------
def track_bus(request, journey_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    journey = Journey.objects.get(id=journey_id)
    return render(request, "track_bus.html", {"journey": journey})


# -------------------------
# LATEST LOCATION API
# -------------------------
def latest_location(request, journey_id):
    try:
        location = BusLocation.objects.filter(journey_id=journey_id).latest("timestamp")
        return JsonResponse({
            "latitude": location.latitude,
            "longitude": location.longitude,
            "timestamp": location.timestamp
        })
    except BusLocation.DoesNotExist:
        return JsonResponse({"error": "No location yet"}, status=404)
