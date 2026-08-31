from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================

    path(
        "",
        views.home,
        name="home",
    ),

    # =====================================================
    # TRIAL BOOKING
    # =====================================================

    path(
        "book-trial/",
        views.trial_booking,
        name="trial_booking",
    ),

    path(
        "booking-success/",
        views.booking_success,
        name="booking_success",
    ),

    # =====================================================
    # DANDIYA REGISTRATION
    # =====================================================

    path(
        "dandiya/<int:event_id>/register/",
        views.dandiya_registration,
        name="dandiya_registration",
    ),

    path(
        "dandiya/registration-success/",
        views.dandiya_registration_success,
        name="dandiya_registration_success",
    ),

    # =====================================================
    # DANDIYA CHECK-IN
    # =====================================================

    path(
        "dandiya/check-in/",
        views.dandiya_checkin,
        name="dandiya_checkin",
    ),

]