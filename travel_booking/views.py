from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import json
import re

from .models import TravelOption, Booking, UserProfile

def home(request):
    """Home page with search functionality"""
    # Get search parameters from request
    source = request.GET.get('source', '').strip()
    destination = request.GET.get('destination', '').strip()
    travel_type = request.GET.get('travel_type', '').strip()
    departure_date = request.GET.get('departure_date', '').strip()
    
    # Start with available travel options
    travel_options = TravelOption.objects.filter(
        departure_datetime__gt=timezone.now(),
        available_seats__gt=0
    )
    
    # Apply filters if provided
    if source:
        travel_options = travel_options.filter(source__icontains=source)
    
    if destination:
        travel_options = travel_options.filter(destination__icontains=destination)
    
    if travel_type and travel_type in ['flight', 'train', 'bus']:
        travel_options = travel_options.filter(travel_type=travel_type)
    
    if departure_date:
        try:
            date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
            travel_options = travel_options.filter(departure_datetime__date=date_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    # Pagination
    paginator = Paginator(travel_options, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'travel_options': page_obj,
        'today': timezone.now().date(),
        'search_data': {
            'source': source,
            'destination': destination,
            'travel_type': travel_type,
            'departure_date': departure_date,
        }
    }
    
    return render(request, 'travel_booking/home.html', context)

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        errors = {}
        
        # Validation
        if not username:
            errors['username'] = 'Username is required.'
        elif len(username) > 150:
            errors['username'] = 'Username cannot exceed 150 characters.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'
        elif not re.match(r'^[a-zA-Z0-9@.+_-]+$', username):
            errors['username'] = 'Username can only contain letters, digits and @/./+/-/_ characters.'
        
        if not first_name:
            errors['first_name'] = 'First name is required.'
        elif len(first_name) > 30:
            errors['first_name'] = 'First name cannot exceed 30 characters.'
        
        if not last_name:
            errors['last_name'] = 'Last name is required.'
        elif len(last_name) > 30:
            errors['last_name'] = 'Last name cannot exceed 30 characters.'
        
        if not email:
            errors['email'] = 'Email is required.'
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors['email'] = 'Email already exists.'
            except ValidationError:
                errors['email'] = 'Enter a valid email address.'
        
        if not password1:
            errors['password1'] = 'Password is required.'
        elif len(password1) < 8:
            errors['password1'] = 'Password must be at least 8 characters long.'
        elif password1.isdigit():
            errors['password1'] = 'Password cannot be entirely numeric.'
        elif password1.lower() in ['password', '12345678', username.lower()]:
            errors['password1'] = 'Password is too common.'
        
        if password1 != password2:
            errors['password2'] = 'Passwords do not match.'
        
        if not errors:
            try:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                # Login user
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to Travel Booking.')
                return redirect('profile')
                
            except Exception as e:
                errors['general'] = 'An error occurred during registration. Please try again.'
        
        # Return form with errors
        return render(request, 'registration/register.html', {
            'errors': errors,
            'form_data': {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
            }
        })
    
    return render(request, 'registration/register.html')

@login_required
def logout_user(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile(request):
    """User profile management"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        date_of_birth = request.POST.get('date_of_birth', '').strip()
        
        errors = {}
        
        # Validation
        if not first_name:
            errors['first_name'] = 'First name is required.'
        elif len(first_name) > 30:
            errors['first_name'] = 'First name cannot exceed 30 characters.'
        
        if not last_name:
            errors['last_name'] = 'Last name is required.'
        elif len(last_name) > 30:
            errors['last_name'] = 'Last name cannot exceed 30 characters.'
        
        if not email:
            errors['email'] = 'Email is required.'
        else:
            try:
                validate_email(email)
                # Check if email exists for other users
                if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    errors['email'] = 'Email already exists.'
            except ValidationError:
                errors['email'] = 'Enter a valid email address.'
        
        if phone_number and not re.match(r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$', phone_number):
            errors['phone_number'] = 'Enter a valid phone number.'
        
        if date_of_birth:
            try:
                birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                if birth_date >= timezone.now().date():
                    errors['date_of_birth'] = 'Date of birth must be in the past.'
                elif birth_date < timezone.now().date() - timedelta(days=36500):  # 100 years
                    errors['date_of_birth'] = 'Please enter a valid date of birth.'
            except ValueError:
                errors['date_of_birth'] = 'Enter a valid date.'
        
        if not errors:
            try:
                # Update user
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email
                request.user.save()
                
                # Update profile
                profile.phone_number = phone_number or None
                profile.address = address or None
                if date_of_birth:
                    profile.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                else:
                    profile.date_of_birth = None
                profile.save()
                
                messages.success(request, 'Profile updated successfully!')
                return redirect('home')
                
            except Exception as e:
                errors['general'] = 'An error occurred while updating profile. Please try again.'
        
        # Return form with errors
        return render(request, 'travel_booking/profile.html', {
            'errors': errors,
            'form_data': {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'date_of_birth': date_of_birth,
            }
        })
    
    # GET request - populate form with current data
    form_data = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'phone_number': profile.phone_number or '',
        'address': profile.address or '',
        'date_of_birth': profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else '',
    }
    
    return render(request, 'travel_booking/profile.html', {'form_data': form_data})

def travel_detail(request, travel_id):
    """Travel option detail view"""
    travel_option = get_object_or_404(TravelOption, travel_id=travel_id)
    return render(request, 'travel_booking/travel_detail.html', {
        'travel_option': travel_option
    })

@login_required
def book_travel(request, travel_id):
    """Book a travel option"""
    travel_option = get_object_or_404(TravelOption, travel_id=travel_id)
    
    if not travel_option.is_available:
        messages.error(request, 'This travel option is no longer available.')
        return redirect('travel_detail', travel_id=travel_id)
    
    if request.method == 'POST':
        # Get form data
        number_of_seats = request.POST.get('number_of_seats', '').strip()
        passenger_names = request.POST.get('passenger_names', '').strip()
        terms_accepted = request.POST.get('terms', '') == 'on'
        
        errors = {}
        
        # Validation
        try:
            seats = int(number_of_seats)
            if seats < 1:
                errors['number_of_seats'] = 'Number of seats must be at least 1.'
            elif seats > travel_option.available_seats:
                errors['number_of_seats'] = f'Only {travel_option.available_seats} seats available.'
            elif seats > 10:
                errors['number_of_seats'] = 'Maximum 10 seats can be booked at once.'
        except (ValueError, TypeError):
            errors['number_of_seats'] = 'Enter a valid number of seats.'
            seats = 0
        
        if not passenger_names:
            errors['passenger_names'] = 'Passenger names are required.'
        else:
            passenger_list = [name.strip() for name in passenger_names.split('\n') if name.strip()]
            
            if len(passenger_list) != seats:
                errors['passenger_names'] = f'Number of passenger names ({len(passenger_list)}) must match number of seats ({seats}).'
            
            # Validate individual names
            for i, name in enumerate(passenger_list):
                if not name:
                    errors['passenger_names'] = f'Passenger name on line {i+1} is empty.'
                    break
                elif len(name) < 2:
                    errors['passenger_names'] = f'Passenger name on line {i+1} is too short.'
                    break
                elif len(name) > 100:
                    errors['passenger_names'] = f'Passenger name on line {i+1} is too long.'
                    break
                elif not re.match(r'^[a-zA-Z\s\.]+$', name):
                    errors['passenger_names'] = f'Passenger name on line {i+1} contains invalid characters.'
                    break
        
        if not terms_accepted:
            errors['terms'] = 'You must accept the terms and conditions.'
        
        if not errors:
            try:
                with transaction.atomic():
                    # Lock the travel option to prevent race conditions
                    travel_option = TravelOption.objects.select_for_update().get(
                        travel_id=travel_id
                    )
                    
                    # Check availability again
                    if travel_option.available_seats < seats:
                        errors['number_of_seats'] = 'Not enough seats available.'
                    else:
                        # Create booking
                        booking = Booking.objects.create(
                            user=request.user,
                            travel_option=travel_option,
                            number_of_seats=seats,
                            total_price=travel_option.price * seats,
                            passenger_details=passenger_list
                        )
                        
                        # Update available seats
                        travel_option.available_seats -= seats
                        travel_option.save()
                        
                        messages.success(request, f'Booking confirmed! Booking ID: #{booking.booking_id}')
                        return redirect('booking_detail', booking_id=booking.booking_id)
                        
            except Exception as e:
                errors['general'] = 'An error occurred while processing your booking. Please try again.'
        
        # Return form with errors
        return render(request, 'travel_booking/book_travel.html', {
            'travel_option': travel_option,
            'errors': errors,
            'form_data': {
                'number_of_seats': number_of_seats,
                'passenger_names': passenger_names,
                'terms_accepted': terms_accepted,
            }
        })
    
    return render(request, 'travel_booking/book_travel.html', {
        'travel_option': travel_option
    })

@login_required
def my_bookings(request):
    """View user's bookings"""
    bookings = Booking.objects.filter(user=request.user)
    
    # Filter by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter in ['confirmed', 'cancelled']:
        bookings = bookings.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'travel_booking/my_bookings.html', {
        'page_obj': page_obj,
        'bookings': page_obj,
        'status_filter': status_filter,
    })

@login_required
def booking_detail(request, booking_id):
    """Booking detail view"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'travel_booking/booking_detail.html', {
        'booking': booking
    })

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if not booking.can_cancel:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirm_cancel', '').strip()
        
        if confirmation != 'yes':
            messages.error(request, 'Booking cancellation was not confirmed.')
            return redirect('cancel_booking', booking_id=booking_id)
        
        try:
            with transaction.atomic():
                # Update booking status
                booking.status = 'cancelled'
                booking.save()
                
                # Restore available seats
                travel_option = booking.travel_option
                travel_option.available_seats += booking.number_of_seats
                travel_option.save()
                
            messages.success(request, 'Booking cancelled successfully.')
            return redirect('my_bookings')
            
        except Exception as e:
            messages.error(request, 'An error occurred while cancelling booking. Please try again.')
            return redirect('cancel_booking', booking_id=booking_id)
    
    return render(request, 'travel_booking/cancel_booking.html', {
        'booking': booking
    })

def search_cities(request):
    """AJAX endpoint for city search autocomplete"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # Get unique cities from travel options
    sources = list(TravelOption.objects.filter(
        source__icontains=query
    ).values_list('source', flat=True).distinct()[:5])
    
    destinations = list(TravelOption.objects.filter(
        destination__icontains=query
    ).values_list('destination', flat=True).distinct()[:5])
    
    # Combine and deduplicate
    cities = list(set(sources + destinations))[:10]
    return JsonResponse(sorted(cities), safe=False)

# Custom login view to handle form data manually
def custom_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('rememberMe', '') == 'on'
        
        errors = {}
        
        if not username:
            errors['username'] = 'Username is required.'
        
        if not password:
            errors['password'] = 'Password is required.'
        
        if not errors:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiry based on remember me
                if not remember_me:
                    request.session.set_expiry(0)  # Browser session
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Redirect to next or home
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                errors['general'] = 'Invalid username or password.'
        
        return render(request, 'registration/login.html', {
            'errors': errors,
            'form_data': {
                'username': username,
                'remember_me': remember_me,
            }
        })
    
    return render(request, 'registration/login.html')