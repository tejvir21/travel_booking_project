from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class TravelOption(models.Model):
    TRAVEL_TYPES = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
    ]
    
    travel_id = models.AutoField(primary_key=True)
    travel_type = models.CharField(max_length=10, choices=TRAVEL_TYPES)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    operator = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['departure_datetime']

    def __str__(self):
        return f"{self.get_travel_type_display()} - {self.source} to {self.destination}"

    @property
    def is_available(self):
        return self.available_seats > 0 and self.departure_datetime > timezone.now()

    def get_duration(self):
        """Calculate travel duration"""
        duration = self.arrival_datetime - self.departure_datetime
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE, related_name='bookings')
    number_of_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    passenger_details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking #{self.booking_id} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.travel_option.price * self.number_of_seats
        super().save(*args, **kwargs)

    @property
    def can_cancel(self):
        """Check if booking can be cancelled (at least 2 hours before departure)"""
        if self.status == 'cancelled':
            return False
        time_until_departure = self.travel_option.departure_datetime - timezone.now()
        return time_until_departure.total_seconds() > 7200  # 2 hours in seconds