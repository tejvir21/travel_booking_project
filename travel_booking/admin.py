from django.contrib import admin
from .models import UserProfile, TravelOption, Booking

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('created_at',)

@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ('travel_id', 'travel_type', 'source', 'destination', 
                   'departure_datetime', 'price', 'available_seats', 'is_available')
    list_filter = ('travel_type', 'departure_datetime', 'source', 'destination')
    search_fields = ('source', 'destination', 'operator')
    date_hierarchy = 'departure_datetime'
    ordering = ('departure_datetime',)
    
    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'Available'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'travel_option', 'number_of_seats', 
                   'total_price', 'status', 'booking_date')
    list_filter = ('status', 'booking_date', 'travel_option__travel_type')
    search_fields = ('user__username', 'user__email', 'booking_id')
    date_hierarchy = 'booking_date'
    readonly_fields = ('booking_id', 'total_price', 'booking_date')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'travel_option', 'number_of_seats')
        return self.readonly_fields