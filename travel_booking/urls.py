from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('travel/<int:travel_id>/', views.travel_detail, name='travel_detail'),
    path('book/<int:travel_id>/', views.book_travel, name='book_travel'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('profile/', views.profile, name='profile'),
    path('ajax/search-cities/', views.search_cities, name='search_cities'),
]
