import uuid

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from .forms import (
    TrialBookingForm,
    DandiyaRegistrationForm,
    DandiyaCheckInForm,
)

from .models import (
    DanceClass,
    GalleryImage,
    Schedule,
    Testimonial,
    DandiyaEvent,
    DandiyaRegistration,
)


# =========================================================
# HOME
# =========================================================

def home(request):

    classes = DanceClass.objects.filter(
        is_active=True
    )

    schedules = Schedule.objects.select_related(
        "dance_class"
    )

    gallery_images = GalleryImage.objects.filter(
        is_active=True
    )

    testimonials = Testimonial.objects.filter(
        is_active=True
    )

    dandiya_events = (
        DandiyaEvent.objects
        .filter(is_active=True)
        .prefetch_related(
            "passes",
            "sponsors",
        )
    )

    context = {
        "classes": classes,
        "schedules": schedules,
        "gallery_images": gallery_images,
        "testimonials": testimonials,
        "dandiya_events": dandiya_events,
    }

    return render(
        request,
        "home.html",
        context,
    )


# =========================================================
# TRIAL BOOKING
# =========================================================

def trial_booking(request):

    if request.method == "POST":

        form = TrialBookingForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("booking_success")

    else:

        form = TrialBookingForm()

    return render(
        request,
        "trial_booking.html",
        {
            "form": form,
        },
    )


# =========================================================
# BOOKING SUCCESS
# =========================================================

def booking_success(request):

    return render(
        request,
        "booking_success.html",
    )


# =========================================================
# DANDIYA REGISTRATION
# =========================================================

def dandiya_registration(request, event_id):

    event = get_object_or_404(
        DandiyaEvent,
        id=event_id,
        is_active=True,
    )

    if request.method == "POST":

        form = DandiyaRegistrationForm(
            request.POST,
            event=event,
        )

        if form.is_valid():

            registration = form.save(
                commit=False
            )

            registration.event = event

            # =============================================
            # CALCULATE REGISTRATION AMOUNT
            # =============================================

            registration.total_amount = (
                registration.dandiya_pass.price
                * registration.number_of_participants
            )

            # =============================================
            # GENERATE UNIQUE ENTRY CODE
            # =============================================

            while True:

                entry_code = (
                    f"WSDC-{event.id}-"
                    f"{uuid.uuid4().hex[:8].upper()}"
                )

                if not DandiyaRegistration.objects.filter(
                    entry_code=entry_code
                ).exists():
                    break

            registration.entry_code = entry_code

            # =============================================
            # SAVE REGISTRATION
            # =============================================

            registration.save()

            request.session["dandiya_registration_id"] = (
                registration.id
            )

            return redirect(
                "dandiya_registration_success"
            )

    else:

        form = DandiyaRegistrationForm(
            event=event,
        )

    return render(
        request,
        "dandiya_registration.html",
        {
            "event": event,
            "form": form,
        },
    )


# =========================================================
# DANDIYA REGISTRATION SUCCESS
# =========================================================

def dandiya_registration_success(request):

    registration_id = request.session.pop(
        "dandiya_registration_id",
        None,
    )

    registration = None

    if registration_id:

        registration = (
            DandiyaRegistration.objects
            .select_related(
                "event",
                "dandiya_pass",
            )
            .filter(
                id=registration_id,
            )
            .first()
        )

    return render(
        request,
        "dandiya_registration_success.html",
        {
            "registration": registration,
        },
    )


# =========================================================
# DANDIYA CHECK-IN
# =========================================================

def dandiya_checkin(request):

    registration = None
    checked = False

    if request.method == "POST":

        form = DandiyaCheckInForm(
            request.POST
        )

        if form.is_valid():

            entry_code = form.cleaned_data[
                "entry_code"
            ]

            registration = (
                DandiyaRegistration.objects
                .select_related(
                    "event",
                    "dandiya_pass",
                )
                .filter(
                    entry_code__iexact=entry_code,
                )
                .first()
            )

            if registration is None:

                form.add_error(
                    "entry_code",
                    "No registration found with this entry code.",
                )

            else:

                checked = True

    else:

        form = DandiyaCheckInForm()

    return render(
        request,
        "dandiya_checkin.html",
        {
            "form": form,
            "registration": registration,
            "checked": checked,
        },
    )