import base64
import uuid

from io import BytesIO

import qrcode

from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone

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

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
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
                * registration.number_of_passes
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
            #
            # DandiyaRegistration.save() automatically
            # generates coupon_token for new registrations.
            #
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

    registration_id = request.session.get(
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
# DANDIYA COUPON
# =========================================================
#
# PUBLIC CUSTOMER COUPON
#
# The coupon is accessed through a random coupon_token.
#
# Example:
#
# /dandiya/coupon/<coupon-token>/
#
# The token does NOT expose the database ID.
#
# IMPORTANT:
#
# A coupon is considered valid only after the WSDC team
# verifies the payment and changes payment_status to Paid.
#
# =========================================================

def dandiya_coupon(request, coupon_token):

    registration = get_object_or_404(
        DandiyaRegistration.objects.select_related(
            "event",
            "dandiya_pass",
        ),
        coupon_token=coupon_token,
    )

    # =====================================================
    # PAYMENT NOT VERIFIED
    # =====================================================

    if registration.payment_status != (
        DandiyaRegistration.PaymentStatus.PAID
    ):

        return render(
            request,
            "dandiya_coupon.html",
            {
                "registration": registration,
                "coupon_valid": False,
            },
        )

    # =====================================================
    # GENERATE QR CODE
    # =====================================================
    #
    # The QR contains ONLY the unique entry code.
    #
    # Personal information and payment information stay
    # inside the Django database.
    #
    # =====================================================

    qr_image = qrcode.make(
        registration.entry_code
    )

    qr_buffer = BytesIO()

    qr_image.save(
        qr_buffer,
        format="PNG",
    )

    qr_base64 = base64.b64encode(
        qr_buffer.getvalue()
    ).decode("utf-8")

    # =====================================================
    # GENERATE SECURE ABSOLUTE COUPON URL
    # =====================================================
    #
    # This automatically becomes:
    #
    # Local:
    # http://127.0.0.1:8000/dandiya/coupon/...
    #
    # Production:
    # https://dance-academy-jwmz.onrender.com/dandiya/coupon/...
    #
    # The coupon token is used instead of the database ID.
    #
    # =====================================================

    coupon_url = request.build_absolute_uri(
        reverse(
            "dandiya_coupon",
            kwargs={
                "coupon_token": registration.coupon_token,
            },
        )
    )

    return render(
        request,
        "dandiya_coupon.html",
        {
            "registration": registration,
            "coupon_valid": True,
            "qr_base64": qr_base64,
            "coupon_url": coupon_url,
        },
    )


# =========================================================
# DANDIYA COUPON PDF
# =========================================================
#
# Generates a downloadable PDF coupon for PAID registrations.
#
# The PDF is generated in memory.
# Nothing is permanently stored on the Render filesystem.
#
# =========================================================

def dandiya_coupon_pdf(request, coupon_token):

    registration = get_object_or_404(
        DandiyaRegistration.objects.select_related(
            "event",
            "dandiya_pass",
        ),
        coupon_token=coupon_token,
    )

    # =====================================================
    # PAYMENT CHECK
    # =====================================================

    if registration.payment_status != (
        DandiyaRegistration.PaymentStatus.PAID
    ):

        return render(
            request,
            "dandiya_coupon.html",
            {
                "registration": registration,
                "coupon_valid": False,
            },
        )

    # =====================================================
    # CREATE PDF IN MEMORY
    # =====================================================

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CouponTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=24,
        leading=28,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "CouponSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        leading=16,
        spaceAfter=6,
    )

    heading_style = ParagraphStyle(
        "CouponHeading",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=16,
        leading=20,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "CouponNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
    )

    center_style = ParagraphStyle(
        "CouponCenter",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=15,
    )

    entry_style = ParagraphStyle(
        "CouponEntry",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=15,
        leading=20,
        spaceBefore=8,
        spaceAfter=8,
    )

    story = []

    # =====================================================
    # HEADER
    # =====================================================

    story.append(
        Paragraph(
            "WSDC DANDIYA NIGHT",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "Dandiya Entry Coupon",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "✓ PAYMENT VERIFIED",
            heading_style,
        )
    )

    story.append(Spacer(1, 10))

    # =====================================================
    # EVENT DETAILS
    # =====================================================

    story.append(
        Paragraph(
            registration.event.name,
            heading_style,
        )
    )

    event_date = registration.event.event_date.strftime(
        "%d %B %Y"
    )

    story.append(
        Paragraph(
            f"Date: {event_date}",
            center_style,
        )
    )

    if registration.event.start_time:

        start_time = registration.event.start_time.strftime(
            "%I:%M %p"
        ).lstrip("0")

        time_text = f"Time: {start_time}"

        if registration.event.end_time:

            end_time = registration.event.end_time.strftime(
                "%I:%M %p"
            ).lstrip("0")

            time_text += f" - {end_time}"

        story.append(
            Paragraph(
                time_text,
                center_style,
            )
        )

    story.append(
        Paragraph(
            f"Venue: {registration.event.venue}",
            center_style,
        )
    )

    story.append(Spacer(1, 20))

    # =====================================================
    # GENERATE ENTRY QR
    # =====================================================

    qr_image = qrcode.make(
        registration.entry_code
    )

    qr_buffer = BytesIO()

    qr_image.save(
        qr_buffer,
        format="PNG",
    )

    qr_buffer.seek(0)

    story.append(
        Paragraph(
            "Scan this QR code at the entrance",
            center_style,
        )
    )

    story.append(Spacer(1, 8))

    qr = Image(
        qr_buffer,
        width=170,
        height=170,
    )

    story.append(qr)

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "This QR code is unique to this registration.",
            center_style,
        )
    )

    story.append(Spacer(1, 15))

    # =====================================================
    # ENTRY CODE
    # =====================================================

    story.append(
        Paragraph(
            f"<b>ENTRY CODE</b><br/>{registration.entry_code}",
            entry_style,
        )
    )

    story.append(
        Paragraph(
            "Keep this code as a backup if the QR scanner "
            "cannot be used.",
            center_style,
        )
    )

    story.append(Spacer(1, 20))

    # =====================================================
    # CUSTOMER / PAYMENT DETAILS
    # =====================================================

    details = [
        [
            Paragraph("<b>Name</b>", normal_style),
            Paragraph(
                str(registration.name),
                normal_style,
            ),
        ],
        [
            Paragraph("<b>Pass</b>", normal_style),
            Paragraph(
                str(registration.dandiya_pass.name),
                normal_style,
            ),
        ],
        [
            Paragraph("<b>Number of Passes</b>", normal_style),
            Paragraph(
                str(registration.number_of_passes),
                normal_style,
            ),
        ],
        [
            Paragraph("<b>Total Paid</b>", normal_style),
            Paragraph(
                f"₹{registration.total_amount:.0f}",
                normal_style,
            ),
        ],
        [
            Paragraph("<b>Payment Status</b>", normal_style),
            Paragraph(
                "PAID / VERIFIED",
                normal_style,
            ),
        ],
    ]

    details_table = Table(
        details,
        colWidths=[150, 320],
    )

    details_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.whitesmoke,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(details_table)

    story.append(Spacer(1, 20))

    # =====================================================
    # ENTRY INSTRUCTIONS
    # =====================================================

    story.append(
        Paragraph(
            "<b>ENTRY INSTRUCTIONS</b>",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Show this coupon or the QR code at the "
            "WSDC Dandiya Night entrance.",
            center_style,
        )
    )

    story.append(
        Paragraph(
            "This ticket can be used for entry only once.",
            center_style,
        )
    )

    story.append(
        Paragraph(
            "After successful check-in, this ticket cannot "
            "be used again.",
            center_style,
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "WSDC • Dance • Fitness • Wellness",
            center_style,
        )
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(story)

    pdf_buffer.seek(0)

    response = HttpResponse(
        pdf_buffer.getvalue(),
        content_type="application/pdf",
    )

    response[
        "Content-Disposition"
    ] = (
        f'inline; '
        f'filename="WSDC-Dandiya-Coupon-'
        f'{registration.entry_code}.pdf"'
    )

    return response


# =========================================================
# DANDIYA CHECK-IN
# =========================================================
#
# STAFF ONLY
#
# This page is used by WSDC staff at the event entrance.
#
# Rules:
#
# 1. Registration must exist.
# 2. Payment must be Paid.
# 3. Registration must not already be checked in.
# 4. A successful check-in is immediately marked as used.
# 5. Database row locking prevents duplicate approval
#    when two requests arrive at almost the same time.
#
# =========================================================

@staff_member_required
def dandiya_checkin(request):

    registration = None
    checked = False
    checkin_result = None

    if request.method == "POST":

        form = DandiyaCheckInForm(
            request.POST
        )

        if form.is_valid():

            entry_code = form.cleaned_data[
                "entry_code"
            ]

            # =============================================
            # ATOMIC CHECK-IN
            # =============================================

            with transaction.atomic():

                registration = (
                    DandiyaRegistration.objects
                    .select_for_update()
                    .select_related(
                        "event",
                        "dandiya_pass",
                    )
                    .filter(
                        entry_code__iexact=entry_code,
                    )
                    .first()
                )

                # =========================================
                # INVALID CODE
                # =========================================

                if registration is None:

                    checkin_result = "invalid"

                    form.add_error(
                        "entry_code",
                        "No registration found with this entry code.",
                    )

                # =========================================
                # ALREADY CHECKED IN
                # =========================================

                elif registration.checked_in:

                    checkin_result = "already_used"

                # =========================================
                # PAYMENT NOT VERIFIED
                # =========================================

                elif registration.payment_status != (
                    DandiyaRegistration.PaymentStatus.PAID
                ):

                    if registration.payment_status == (
                        DandiyaRegistration.PaymentStatus.PENDING
                    ):

                        checkin_result = "payment_pending"

                    else:

                        checkin_result = "payment_failed"

                # =========================================
                # ENTRY APPROVED
                # =========================================

                else:

                    registration.checked_in = True
                    registration.checked_in_at = timezone.now()

                    registration.save(
                        update_fields=[
                            "checked_in",
                            "checked_in_at",
                        ]
                    )

                    checkin_result = "approved"
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
            "checkin_result": checkin_result,
        },
    )