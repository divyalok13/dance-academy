from django.db import models
import uuid


# =========================================================
# DANCE CLASSES
# =========================================================

class DanceClass(models.Model):

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField()

    age_group = models.CharField(
        max_length=100,
        blank=True,
    )

    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    image = models.ImageField(
        upload_to="classes/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# CLASS SCHEDULE
# =========================================================

class Schedule(models.Model):

    class Day(models.TextChoices):
        MONDAY = "Monday", "Monday"
        TUESDAY = "Tuesday", "Tuesday"
        WEDNESDAY = "Wednesday", "Wednesday"
        THURSDAY = "Thursday", "Thursday"
        FRIDAY = "Friday", "Friday"
        SATURDAY = "Saturday", "Saturday"
        SUNDAY = "Sunday", "Sunday"

    dance_class = models.ForeignKey(
        DanceClass,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    day = models.CharField(
        max_length=10,
        choices=Day.choices,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return (
            f"{self.dance_class.name} - "
            f"{self.day} "
            f"{self.start_time.strftime('%I:%M %p')} - "
            f"{self.end_time.strftime('%I:%M %p')}"
        )


# =========================================================
# GALLERY
# =========================================================

class GalleryImage(models.Model):

    title = models.CharField(
        max_length=150,
        blank=True,
    )

    image = models.ImageField(
        upload_to="gallery/",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Gallery Image {self.pk}"


# =========================================================
# TESTIMONIALS
# =========================================================

class Testimonial(models.Model):

    name = models.CharField(
        max_length=100,
    )

    message = models.TextField()

    rating = models.PositiveSmallIntegerField(
        default=5,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# =========================================================
# TRIAL BOOKINGS
# =========================================================

class TrialBooking(models.Model):

    name = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=20,
    )

    email = models.EmailField(
        blank=True,
    )

    dance_class = models.ForeignKey(
        DanceClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trial_bookings",
    )

    preferred_date = models.DateField(
        null=True,
        blank=True,
    )

    message = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.phone}"


# =========================================================
# DANDIYA EVENTS
# =========================================================

class DandiyaEvent(models.Model):

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    event_date = models.DateField()

    start_time = models.TimeField(
        null=True,
        blank=True,
    )

    end_time = models.TimeField(
        null=True,
        blank=True,
    )

    venue = models.CharField(
        max_length=255,
    )

    group_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Group discount percentage. Keep 0 until decided.",
    )

    image = models.ImageField(
        upload_to="dandiya/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["event_date"]

    def __str__(self):
        return self.name


# =========================================================
# DANDIYA PASSES
# =========================================================

class DandiyaPass(models.Model):

    event = models.ForeignKey(
        DandiyaEvent,
        on_delete=models.CASCADE,
        related_name="passes",
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    number_of_people = models.PositiveIntegerField(
        default=1,
        help_text="Number of people covered by this pass.",
    )

    is_active = models.BooleanField(
        default=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["display_order", "price"]

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


# =========================================================
# DANDIYA SPONSORS
# =========================================================

class DandiyaSponsor(models.Model):

    event = models.ForeignKey(
        DandiyaEvent,
        on_delete=models.CASCADE,
        related_name="sponsors",
    )

    name = models.CharField(
        max_length=150,
    )

    logo = models.ImageField(
        upload_to="dandiya/sponsors/",
        blank=True,
        null=True,
    )

    website = models.URLField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


# =========================================================
# DANDIYA REGISTRATIONS
# =========================================================

class DandiyaRegistration(models.Model):

    class PaymentStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        PAID = "Paid", "Paid"
        FAILED = "Failed", "Failed"

    event = models.ForeignKey(
        DandiyaEvent,
        on_delete=models.CASCADE,
        related_name="registrations",
    )

    dandiya_pass = models.ForeignKey(
        DandiyaPass,
        on_delete=models.PROTECT,
        related_name="registrations",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=20,
    )

    email = models.EmailField(
        blank=True,
    )

    age = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    number_of_participants = models.PositiveIntegerField(
        default=1,
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    payment_id = models.CharField(
        max_length=255,
        blank=True,
    )

    entry_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
    )

    message = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        # Generate an entry code only when creating
        # a new registration.
        if not self.entry_code:

            while True:

                code = (
                    f"WSDC-DAN-"
                    f"{uuid.uuid4().hex[:8].upper()}"
                )

                if not DandiyaRegistration.objects.filter(
                    entry_code=code
                ).exists():

                    self.entry_code = code
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.entry_code}"