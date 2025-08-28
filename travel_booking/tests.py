from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import UserProfile, TravelOption, Booking

# Create your tests here.

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_creation(self):
        """Test that profile is created with user"""
        profile = UserProfile.objects.create(
            user=self.user,
            phone_number='+91-9876543210',
            address='Test Address'
        )
        self.assertEqual(str(profile), "testuser's Profile")
        self.assertEqual(profile.user, self.user)

class TravelOptionModelTest(TestCase):
    def setUp(self):
        self.departure_time = timezone.now() + timedelta(hours=24)
        self.arrival_time = self.departure_time + timedelta(hours=2)
        
        self.travel_option = TravelOption.objects.create(
            travel_type='flight',
            source='Delhi',
            destination='Mumbai',
            departure_datetime=self.departure_time,
            arrival_datetime=self.arrival_time,
            price=Decimal('5000.00'),
            available_seats=100,
            total_seats=100,
            operator='Test Airlines'
        )

    def test_travel_option_creation(self):
        """Test travel option creation and string representation"""
        self.assertEqual(str(self.travel_option), 'Flight - Delhi to Mumbai')
        self.assertTrue(self.travel_option.is_available)
        self.assertEqual(self.travel_option.get_duration(), '2h 0m')

    def test_is_available_property(self):
        """Test is_available property"""
        # Should be available initially
        self.assertTrue(self.travel_option.is_available)
        
        # Should not be available if no seats
        self.travel_option.available_seats = 0
        self.travel_option.save()
        self.assertFalse(self.travel_option.is_available)
        
        # Should not be available if in the past
        self.travel_option.available_seats = 10
        self.travel_option.departure_datetime = timezone.now() - timedelta(hours=1)
        self.travel_option.save()
        self.assertFalse(self.travel_option.is_available)

class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        departure_time = timezone.now() + timedelta(hours=24)
        arrival_time = departure_time + timedelta(hours=2)
        
        self.travel_option = TravelOption.objects.create(
            travel_type='flight',
            source='Delhi',
            destination='Mumbai',
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            price=Decimal('5000.00'),
            available_seats=100,
            total_seats=100,
            operator='Test Airlines'
        )

    def test_booking_creation(self):
        """Test booking creation"""
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=2,
            passenger_details=['John Doe', 'Jane Doe']
        )
        
        self.assertEqual(str(booking), f'Booking #{booking.booking_id} - testuser')
        self.assertEqual(booking.total_price, Decimal('10000.00'))  # 2 * 5000
        self.assertTrue(booking.can_cancel)

    def test_can_cancel_property(self):
        """Test can_cancel property"""
        # Create booking for future travel
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=1,
        )
        self.assertTrue(booking.can_cancel)
        
        # Cancel the booking
        booking.status = 'cancelled'
        booking.save()
        self.assertFalse(booking.can_cancel)
        
        # Test booking for past travel (less than 2 hours)
        past_travel = TravelOption.objects.create(
            travel_type='bus',
            source='Delhi',
            destination='Agra',
            departure_datetime=timezone.now() + timedelta(minutes=30),
            arrival_datetime=timezone.now() + timedelta(hours=1),
            price=Decimal('500.00'),
            available_seats=40,
            total_seats=40,
            operator='Test Bus'
        )
        
        past_booking = Booking.objects.create(
            user=self.user,
            travel_option=past_travel,
            number_of_seats=1,
        )
        self.assertFalse(past_booking.can_cancel)

class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        departure_time = timezone.now() + timedelta(hours=24)
        arrival_time = departure_time + timedelta(hours=2)
        
        self.travel_option = TravelOption.objects.create(
            travel_type='flight',
            source='Delhi',
            destination='Mumbai',
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            price=Decimal('5000.00'),
            available_seats=100,
            total_seats=100,
            operator='Test Airlines'
        )

    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find Your Perfect Journey')

    def test_travel_search(self):
        """Test travel search functionality"""
        response = self.client.get(reverse('home'), {
            'source': 'Delhi',
            'destination': 'Mumbai',
            'travel_type': 'flight'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delhi → Mumbai')

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'testpass123456',
            'password2': 'testpass123456'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_travel_detail_view(self):
        """Test travel detail view"""
        response = self.client.get(
            reverse('travel_detail', kwargs={'travel_id': self.travel_option.travel_id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delhi → Mumbai')

    def test_booking_requires_login(self):
        """Test that booking requires authentication"""
        response = self.client.get(
            reverse('book_travel', kwargs={'travel_id': self.travel_option.travel_id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_booking_logged_in_user(self):
        """Test booking for logged in user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('book_travel', kwargs={'travel_id': self.travel_option.travel_id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Your Booking')

    def test_booking_creation(self):
        """Test booking creation through form"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('book_travel', kwargs={'travel_id': self.travel_option.travel_id}), {
                'number_of_seats': 2,
                'passenger_names': 'John Doe\nJane Doe'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful booking
        self.assertTrue(Booking.objects.filter(user=self.user).exists())
        
        # Check that seats were decremented
        self.travel_option.refresh_from_db()
        self.assertEqual(self.travel_option.available_seats, 98)

    def test_my_bookings_view(self):
        """Test my bookings view"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a booking first
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=1,
        )
        
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Booking #{booking.booking_id}')

    def test_cancel_booking(self):
        """Test booking cancellation"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a booking
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=2,
        )
        
        # Test GET request (confirmation page)
        response = self.client.get(
            reverse('cancel_booking', kwargs={'booking_id': booking.booking_id})
        )
        self.assertEqual(response.status_code, 200)
        
        # Test POST request (actual cancellation)
        response = self.client.post(
            reverse('cancel_booking', kwargs={'booking_id': booking.booking_id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check that booking was cancelled and seats restored
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        
        self.travel_option.refresh_from_db()
        self.assertEqual(self.travel_option.available_seats, 100)  # Seats restored