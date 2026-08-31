from django.contrib import admin

from .models import (
    DanceClass,
    Schedule,
    GalleryImage,
    Testimonial,
    TrialBooking,
    DandiyaEvent,
    DandiyaPass,
    DandiyaSponsor,
    DandiyaRegistration,
)


# =========================================================
# DANCE CLASS ADMIN
# =========================================================

@admin.register(DanceClass)
class DanceClassAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "age_group",
        "fee",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "age_group",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# SCHEDULE ADMIN
# =========================================================

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):

    list_display = (
        "dance_class",
        "day",
        "start_time",
        "end_time",
    )

    list_filter = (
        "day",
        "dance_class",
    )

    search_fields = (
        "dance_class__name",
    )

    ordering = (
        "day",
        "start_time",
    )


# =========================================================
# GALLERY ADMIN
# =========================================================

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# TESTIMONIAL ADMIN
# =========================================================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "rating",
        "is_active",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_active",
    )

    search_fields = (
        "name",
        "message",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# TRIAL BOOKING ADMIN
# =========================================================

@admin.register(TrialBooking)
class TrialBookingAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "email",
        "dance_class",
        "preferred_date",
        "created_at",
    )

    list_filter = (
        "dance_class",
        "preferred_date",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "message",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# DANDIYA EVENT ADMIN
# =========================================================

@admin.register(DandiyaEvent)
class DandiyaEventAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "event_date",
        "start_time",
        "end_time",
        "venue",
        "group_discount_percent",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "event_date",
    )

    search_fields = (
        "name",
        "description",
        "venue",
    )

    ordering = (
        "event_date",
        "start_time",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# DANDIYA PASS ADMIN
# =========================================================

@admin.register(DandiyaPass)
class DandiyaPassAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "event",
        "price",
        "number_of_people",
        "is_active",
        "display_order",
        "created_at",
    )

    list_filter = (
        "event",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "event__name",
    )

    ordering = (
        "event",
        "display_order",
        "price",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# DANDIYA SPONSOR ADMIN
# =========================================================

@admin.register(DandiyaSponsor)
class DandiyaSponsorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "event",
        "is_active",
        "display_order",
        "created_at",
    )

    list_filter = (
        "event",
        "is_active",
    )

    search_fields = (
        "name",
        "event__name",
        "website",
    )

    ordering = (
        "event",
        "display_order",
        "name",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# DANDIYA REGISTRATION ADMIN
# =========================================================

@admin.register(DandiyaRegistration)
class DandiyaRegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "event",
        "dandiya_pass",
        "number_of_participants",
        "total_amount",
        "payment_status",
        "entry_code",
        "created_at",
    )

    list_filter = (
        "event",
        "dandiya_pass",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "entry_code",
        "payment_id",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "entry_code",
        "payment_id",
        "total_amount",
    )

    list_per_page = 25