import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import *
from django.contrib import messages
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from .forms import *
from .models import *
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from collections import defaultdict
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

def index(request):
    services = Service.objects.all()
    total_users = User.objects.filter(is_client=True).count()
    therapists = User.objects.filter(is_therapist=True)
    educators = Educator.objects.select_related('user').all()
    total_services = services.count() 

    total_therapists = therapists.count()
    total_educators = educators.count()
    total_professionals = total_therapists + total_educators

    return render(request, 'index.html', {
        'services': services,
        'total_users': total_users,
        'therapists': therapists,
        'educators': educators,
        'total_therapists': total_therapists,
        'total_educators': total_educators,
        'total_professionals': total_professionals,
        'total_services': total_services, 
    })

def employee(request):
    return render(request,'employee/employee.html')


@login_required
def admin(request):
    services = Service.objects.all()
    categories = Category.objects.all()
    total_users = User.objects.filter(is_client=True).count()
    all_users = User.objects.exclude(id=request.user.id).filter(is_active=True)

    # Fetch recent enrollments and appointments
    recent_enrollments = Enrollment.objects.filter(status='Enrolled').select_related('schedule', 'educator').order_by('-id')[:5]
    recent_appointments = Appointment.objects.filter(status='Confirmed').select_related('therapist', 'service').order_by('-id')[:5]

    # Count pending appointments
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()

    # Fetch all employees (therapists and educators)
    all_employees = User.objects.filter(is_therapist=True) | User.objects.filter(is_educator=True)

    # Calculate total enrollments and appointments
    total_enrollments = Enrollment.objects.filter(status='Enrolled').count()
    total_appointments = Appointment.objects.filter(status='Confirmed').count()

    # Calculate earnings for the current month
    now = datetime.now()
    start_of_month = now.replace(day=1)

    payments = Payment.objects.filter(
        enrollment__status='Enrolled',
        confirmation_status='Confirmed',
        payment_date__gte=start_of_month,
        payment_date__lte=now
    )
    total_earnings = payments.aggregate(total=Sum('amount'))['total'] or 0
    days_in_month = now.day
    average_earning = int(total_earnings / days_in_month) if days_in_month > 0 else 0

    # Calculate monthly earnings
    monthly_earnings = (
        Payment.objects.filter(confirmation_status='Confirmed')
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    # Prepare data for the chart
    months = [entry['month'].strftime('%b %Y') for entry in monthly_earnings]
    monthly_totals = [float(entry['total']) for entry in monthly_earnings]

    return render(request, 'admin/admin.html', {
        'total_users': total_users,
        'all_users': all_users,
        'services': services,
        'categories': categories,
        'recent_enrollments': recent_enrollments,
        'recent_appointments': recent_appointments,
        'pending_appointments_count': pending_appointments_count,  # Pass to template
        'pending_enrollments_count': pending_enrollments_count,
        'all_employees': all_employees,
        'total_enrollments': total_enrollments,
        'total_appointments': total_appointments,
        'total_earnings': total_earnings,
        'average_earning': average_earning,
        'current_date': now,
        'months': json.dumps(months),  # Serialize to JSON
        'monthly_totals': json.dumps(monthly_totals),  # Serialize to JSON
    })
    
def signup(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  

         
            user.is_admin = False  
            user.is_client = True 
            user.is_employee = False
            user.is_therapist = False
            user.is_educator = False
           

            user.save() 
            msg = 'User created successfully'
            return redirect('login_view')  
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form, 'msg': msg})

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_admin:
                login(request, user)
                return redirect('adminpage')
            elif user is not None and user.is_client:
                login(request, user)
                return redirect('customer',user_id=user.id)
            elif user is not None and user.is_employee:
                login(request, user)
                return redirect('employee')
            elif user is not None and user.is_therapist:
                login(request, user)
                return redirect('therapist_profile')
            elif user is not None and user.is_educator:
                login(request, user)
                return redirect('educator', user_id=user.id)
            else:
                msg= 'invalid credentials'
        else:
            msg = 'error validating form'
    return render(request, 'login.html', {'form': form, 'msg': msg})

def logout_view(request):
    logout(request)  # Ends the user's session
    request.session.flush()
    return redirect('index')  # Redirects to the homepage or login pag

# USER LIST FUNCTIONS
# USER LIST FUNCTIONS
# USER LIST FUNCTIONS
# USER LIST FUNCTIONS
# USER LIST FUNCTIONS

def user_list(request):
    # Count users by role
    therapists = User.objects.filter(is_therapist=True).count()
    educators = User.objects.filter(is_educator=True).count()
    employees = User.objects.filter(is_employee=True).count()
    customers = User.objects.filter(is_client=True).count()

    # Calculate total users
    total_users = User.objects.filter(
        is_therapist=True
    ).count() + User.objects.filter(
        is_educator=True
    ).count() + User.objects.filter(
        is_client=True
    ).count()

    # Other counts
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()

    # Query users with specific roles
    users = User.objects.filter(is_therapist=True) | User.objects.filter(is_educator=True) | User.objects.filter(is_client=True)

    context = {
        'users': users,
        'total_users': total_users,
        'total_therapists': therapists,
        'total_educators': educators,
        'total_employees': employees,
        'total_customers': customers,
        'pending_enrollments_count': pending_enrollments_count,
        'pending_appointments_count': pending_appointments_count,
    }
    return render(request, 'admin/admin_users.html', context)

def validate_user_data(first_name, last_name, username, email, password1, password2, role):
    allowed_roles = ['therapist', 'educator', 'customer']

    if not all([first_name, last_name, username, email, password1, password2, role]):
        return "All fields are required."
    if password1 != password2:
        return "Passwords do not match."
    if role not in allowed_roles:
        return "Invalid role selected."
    if User.objects.filter(username=username).exists():
        return "Username already exists."
    if User.objects.filter(email=email).exists():
        return "Email already exists."
    return None

def add_user(request):
    if request.method == 'POST':
        # Collect form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        # Validate form data
        error_message = validate_user_data(first_name, last_name, username, email, password1, password2, role)
        if error_message:
            messages.error(request, error_message)
            return redirect('user_list')

        try:
            # Create the user
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password1
            )
            # Assign role attribute
            if role == 'therapist':
                user.is_therapist = True
                Therapist.objects.create(user=user)
            elif role == 'educator':
                user.is_educator = True
                # Add entry to Educator table
                Educator.objects.create(user=user)
            elif role == 'customer':
                user.is_client = True
            user.save()

            messages.success(request, "User created successfully.")
            return redirect('user_list')  # Redirect to avoid duplicate submissions
        except ValidationError as e:
            messages.error(request, e.message)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            messages.error(request, "An unexpected error occurred. Please try again.")

    # Reload users to update list on the same page
    users = User.objects.all()
    return render(request, 'admin/admin_users.html', {'users': users})
    
def delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect('user_list')

def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user.address = request.POST.get('address', user.address)
        role = request.POST.get('role')

        # Validation
        if not all([first_name, last_name, username, email, role]):
            messages.error(request, 'Please fill in all required fields.')
        elif password1 and password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, 'Email already exists.')
        else:
            # Update user fields
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email

            if password1:
                user.set_password(password1)  # Update password only if provided

            # Reset all roles to False
            user.is_therapist = False
            user.is_educator = False
            user.is_client = False
            user.is_employee = False

            # Set the selected role to True
            if role == 'therapist':
                user.is_therapist = True
            elif role == 'educator':
                user.is_educator = True
            elif role == 'customer':
                user.is_client = True

            user.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')  # Redirect to the user list view

    # Render the user list page with the updated context
    users = User.objects.all()
    return render(request, 'admin/admin_users.html', {'user': user, 'users': users})

# SERVICES FUNCTIONS
# SERVICES FUNCTIONS
# SERVICES FUNCTIONS
# SERVICES FUNCTIONS
# SERVICES FUNCTIONS

def admin_services(request):
    services = Service.objects.all()
    categories = Category.objects.all()
    therapists = User.objects.filter(is_therapist=True)  # Fetch all therapists
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()


    # Calculate totals
    total_service = services.count()
    total_availability = services.filter(availability=True).count()
    total_therapy = services.filter(category_id__category__iexact="therapy").count()
    total_class = services.filter(category_id__category__iexact="class").count()

    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        therapist_id = request.POST.get('therapist')

        try:
            service = Service.objects.get(id=service_id)
            therapist = User.objects.get(id=therapist_id)

            # Assign the therapist to the service
            service.assigned_therapist = therapist
            service.save()

            messages.success(request, f"Therapist {therapist.first_name} {therapist.last_name} assigned to {service.name}.")
        except (Service.DoesNotExist, User.DoesNotExist):
            messages.error(request, "Service or therapist not found.")

        return redirect('admin_services')

    return render(request, 'admin/admin_services.html', {
        'services': services,
        'categories': categories,
        'therapists': therapists,
        'total_service': total_service,
        'total_availability': total_availability,
        'total_therapy': total_therapy,
        'total_class': total_class,
        'pending_appointments_count': pending_appointments_count,
        'pending_enrollments_count': pending_enrollments_count,
    })

def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_services') 
    else:
        form = ServiceForm()
    return render(request, 'admin/add_service.html', {'form': form})

@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category')
        if category_name:
            # Create and save the new category
            Category.objects.create(category=category_name)
            messages.success(request, "Category added successfully!")
        else:
            messages.error(request, "Category name cannot be empty.")
        return redirect('admin_services')  # Redirect to the services page
    
@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category')
        if category_name:
            # Create and save the new category
            Category.objects.create(category=category_name)
            messages.success(request, "Category added successfully!")
        else:
            messages.error(request, "Category name cannot be empty.")
        return redirect('admin_services')  # Redirect to the services page

def update_service(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        raise Http404("Service does not exist")

    if request.method == 'POST':
        # Update service fields with POST data
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')
        service.availability = request.POST.get('availability') == 'True'
        service.category_id = Category.objects.get(pk=request.POST.get('category_id'))
        service.save()

        # Redirect to services page after update
        return redirect('admin_services')

    categories = Category.objects.all()
    return render(request, 'admin/update_service.html', {'service': service, 'categories': categories})

def delete_service(request, service_id):
    service = Service.objects.get(pk=service_id)
    service.delete()
    return redirect('admin_services')

# ADMIN SCHEDULE FUNCTIONS
# ADMIN SCHEDULE FUNCTIONS
# ADMIN SCHEDULE FUNCTIONS
# ADMIN SCHEDULE FUNCTIONS
# ADMIN SCHEDULE FUNCTIONS

def admin_schedule(request):
    schedules = Schedule.objects.all()
    educators = Educator.objects.all()  # Get all educators
    services = Service.objects.all()  # Get all services
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    return render(request, 'admin/admin_schedule.html', {
        'schedules': schedules,
        'educators': educators,
        'services': services,
        'pending_enrollments_count': pending_enrollments_count,
        'pending_appointments_count': pending_appointments_count,
    })

def add_schedule(request):
    educators = User.objects.filter(is_educator=True)
    services = Service.objects.all()

    if request.method == 'POST':
        educator_id = request.POST.get('educator_id')
        service_id = request.POST.get('service_id')
        day = request.POST.get('day')
        time_start = request.POST.get('time_start')
        time_end = request.POST.get('time_end')

        try:
            # Fetch the specific Educator and Service objects using their IDs
            educator = Educator.objects.get(pk=educator_id)
            service = Service.objects.get(pk=service_id)
            
            # Create a new Schedule instance using educator and service IDs
            new_schedule = Schedule(
                educator=educator,  # Pass the Educator instance here
                service=service,    # Pass the Service instance here
                day=day,
                time_start=time_start,
                time_end=time_end
            )
            new_schedule.save()
            return redirect('admin_schedule')
        except (Educator.DoesNotExist, Service.DoesNotExist):
            # In case the Educator or Service does not exist, handle the error
            return render(request, 'admin/add_schedule.html', {
                'educators': educators,
                'services': services,
                'error': 'Invalid educator or service'
            })

    return render(request, 'admin/add_schedule.html', {'educators': educators, 'services': services})



def edit_schedule(request, schedule_id):
    schedule = Schedule.objects.get(pk=schedule_id)
    educators = Educator.objects.all()  # Fetch Educator instances, not User
    services = Service.objects.all()

    if request.method == 'POST':
        educator_id = request.POST.get('educator_id')
        service_id = request.POST.get('service_id')
        day = request.POST.get('day')
        time_start = request.POST.get('time_start')
        time_end = request.POST.get('time_end')

        try:
            educator = Educator.objects.get(pk=educator_id)  # Fetch Educator, not User
            service = Service.objects.get(pk=service_id)
            schedule.educator_id = educator  # Assign the Educator instance
            schedule.service_id = service
            schedule.day = day
            schedule.time_start = time_start
            schedule.time_end = time_end
            schedule.save()
            return redirect('admin_schedule')
        except (Educator.DoesNotExist, Service.DoesNotExist):
            return render(request, 'admin/edit_schedule.html', {
                'schedule': schedule,
                'educators': educators,
                'services': services,
                'error': 'Invalid educator or service'
            })

    return render(request, 'admin/edit_schedule.html', {
        'schedule': schedule,
        'educators': educators,
        'services': services
    })

def delete_schedule(request, schedule_id):
    schedule = Schedule.objects.get(pk=schedule_id)
    schedule.delete()
    return redirect('admin_schedule')



def admin_display_appointments(request):
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()
    therapists = User.objects.filter(is_therapist=True) 
    appointments = Appointment.objects.select_related('service__assigned_therapist', 'therapist', 'user').all()
    appointments = Appointment.objects.all()
    
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')
        
      
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = new_status
        appointment.save()
        
        messages.success(request, "Appointment status updated successfully.")
        return redirect('admin_appointments')  # Refresh the page after updating

    return render(request, 'admin/admin_display_appointments.html', {'appointments': appointments, 'pending_appointments_count': pending_appointments_count, 'pending_enrollments_count': pending_enrollments_count, 'therapists': therapists,})


# ADMIN FUNCTIONS
# ADMIN FUNCTIONS


def enrollment_list_view(request):
    enrollments = Enrollment.objects.prefetch_related('payment_set').all()
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()
    
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        new_status = request.POST.get('status')
        enrollment = Enrollment.objects.get(id=enrollment_id)
        enrollment.status = new_status
        enrollment.save()
        return redirect('enrollment-list')

    return render(request, 'admin/admin_enrollment_list.html', {'enrollments': enrollments, 'pending_appointments_count': pending_appointments_count, 'pending_enrollments_count': pending_enrollments_count,})

def admin_payments_view(request):
    payments = Payment.objects.select_related('enrollment__client', 'enrollment__educator')
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()

    return render(request, 'admin/admin_payments.html', {'payments': payments, 'pending_appointments_count': pending_appointments_count, 'pending_enrollments_count': pending_enrollments_count,})

def delete_enrollment(request, enrollment_id):
    if request.method == 'POST':
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.delete()
        messages.success(request, "Enrollment deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('enrollment-list')

def update_appointment_status(request, appointment_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = new_status
        appointment.save()
        messages.success(request, "Appointment status updated successfully.")
    return redirect('admin_appointments')  # Replace with your view that lists all appointments

def delete_appointment(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
    return redirect('admin_appointments')


def assign_therapist(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = TherapistAssignmentForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Therapist assigned to {service.name} successfully!")
            return redirect('admin_services')  # Redirect back to the services page
    else:
        form = TherapistAssignmentForm(instance=service)

    return render(request, 'admin/assign_therapist.html', {'form': form, 'service': service})

def update_payment_status(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        new_status = request.POST.get('payment_status')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.payment_status = new_status
            payment.save()
            messages.success(request, "Payment status updated successfully.")
        except Payment.DoesNotExist:
            messages.error(request, "Payment not found.")
    
    return redirect('admin_payments')

# CUSTOMER FUNCTIONS
# CUSTOMER FUNCTIONS
# CUSTOMER FUNCTIONS
# CUSTOMER FUNCTIONS

@login_required
def customer(request, user_id):
    user = get_object_or_404(User, id=user_id)
    admin = User.objects.filter(is_staff=True).first()
    current_date = now()

    if request.method == "POST":
        # Update user details
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.address = request.POST.get("address", user.address)
        user.contact_info = request.POST.get("contact_info", user.contact_info)

        # Handle and save birthdate
        birthdate = request.POST.get("birthdate")
        if birthdate:
            user.birthdate = birthdate

        # Update profile picture if uploaded
        if "profile_picture" in request.FILES:
            user.profile_picture = request.FILES["profile_picture"]

        # Handle password change
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if current_password or new_password1 or new_password2:
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password1 != new_password2:
                messages.error(request, "New passwords do not match.")
            elif not new_password1.strip():  # Ensure password is not empty
                messages.error(request, "New password cannot be empty.")
            else:
                user.set_password(new_password1)
                update_session_auth_hash(request, user)  # Keep user logged in after password change
                messages.success(request, "Password updated successfully.")

        # Save updated details
        try:
            user.save()
            messages.success(request, "Your profile was updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating profile: {e}")

        return redirect("customer", user_id=user.id)

    return render(request, "customer/customer.html", {"user": user, 'admin_id': admin.id})

def customer_classes(request, user_id):
   
    enrollments = Enrollment.objects.filter(client_id=user_id).select_related('schedule__service', 'schedule__educator__user')
    
 
    has_enrolled = enrollments.filter(status="Enrolled").exists()
    
    return render(request, 'customer/customer_classes.html', {
        'enrollments': enrollments,
        'has_enrolled': has_enrolled
    })

def class_resources(request, schedule_id): 
    resources = Resources.objects.filter(schedule_id=schedule_id).select_related('educator__user')
    schedule = get_object_or_404(Schedule, id=schedule_id)

    return render(request, 'customer/class_resources.html', {
        'resources': resources,
        'schedule': schedule
    })



@login_required
def enrollment_view(request, user_id):
    enrolled_classes = Enrollment.objects.filter(client__id=user_id).select_related('schedule', 'educator')

    # Calculate the total price for each enrolled class
    for enrolled_class in enrolled_classes:
        assessment = enrolled_class.assessment_set.first()
        if assessment:
            enrolled_class.total_price = assessment.total_month * assessment.sub_amount
        else:
            enrolled_class.total_price = None  # If no assessment exists

    if request.method == 'POST':
        # Check for cancellation request
        if 'cancel_enrollment' in request.POST:
            enrollment_id = request.POST.get('enrollment_id')
            try:
                enrollment = Enrollment.objects.get(id=enrollment_id, client_id=user_id)
                if enrollment.status == 'Pending':
                    enrollment.status = 'Cancelled'
                    enrollment.save()
                    messages.success(request, 'Enrollment successfully cancelled.')
                else:
                    messages.error(request, 'Only pending enrollments can be cancelled.')
            except Enrollment.DoesNotExist:
                messages.error(request, 'Enrollment not found.')
            return redirect('enrollment', user_id=user_id)

        # Handle new enrollment
        schedule_id = request.POST.get('schedule')
        educator_id = request.POST.get('educator')
        service_id = request.POST.get('service')
        total_months = int(request.POST.get('total_months', 1))

        if not schedule_id or not educator_id or not service_id:
            messages.error(request, "All fields are required to enroll.")
            return redirect('enrollment', user_id=user_id)

        client = get_object_or_404(User, id=user_id)
        educator = get_object_or_404(Educator, id=educator_id)
        schedule = get_object_or_404(Schedule, id=schedule_id)
        service = get_object_or_404(Service, id=service_id)

        # Check if the schedule is open
        if schedule.status != 'Open':
            messages.error(request, "The selected schedule is not available.")
            return redirect('enrollment', user_id=user_id)

        sub_amount = service.price
        total_price = sub_amount * total_months

        enrollment = Enrollment(client=client, educator=educator, schedule=schedule)
        enrollment.save()
        Assessment.objects.create(enrollment=enrollment, total_month=total_months, sub_amount=sub_amount)

        messages.success(request, "Enrollment successful!")
        return redirect('enrollment', user_id=user_id)

    class_category = Category.objects.filter(category__iexact='class').first()
    services = Service.objects.filter(category_id=class_category).prefetch_related(
        Prefetch('schedule_set', queryset=Schedule.objects.filter(status='Open').select_related('educator'))
    ) if class_category else []

    service_schedules = []
    for service in services:
        schedules = service.schedule_set.all()
        service_schedules.append({
            'service': service,
            'schedules': schedules
        })

    return render(request, 'customer/enrollment.html', {
        'service_schedules': service_schedules,
        'user_id': user_id,
        'enrolled_classes': enrolled_classes,
    })

@login_required
def cancel_enrollment(request, enrollment_id):
    if request.method == 'POST':
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, client=request.user)
            if enrollment.status == "Pending":
                enrollment.delete()  # Delete the enrollment
                messages.success(request, 'Your enrollment has been successfully cancelled.')
            else:
                messages.error(request, 'Only pending enrollments can be cancelled.')
        except Enrollment.DoesNotExist:
            messages.error(request, 'Enrollment not found.')

    return redirect('enrollment', user_id=request.user.id)


def calculate_sub_amount(service_id, total_months):
    
    service = Service.objects.get(id=service_id)
    price_per_month = service.price  # Assuming price is per month
    return price_per_month * int(total_months)

@login_required
def customer_therapy(request, user_id):
    user = get_object_or_404(User, id=user_id)
    appointments = Appointment.objects.filter(user=user).order_by('appointment_date')

    return render(request, 'customer/customer_therapy.html', {
        'user': user,
        'appointments': appointments,
    })

def customer_appointment(request, user_id): 
    therapy_category = Category.objects.filter(category__iexact='therapy').first()
    services = Service.objects.filter(category_id=therapy_category) if therapy_category else []
    
    # Define a date range (appointments within the next 30 days)
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)
    
    # Fetch confirmed and pending appointments for the user within the date range
    appointments = Appointment.objects.filter(
        user_id=user_id,
        appointment_date__range=(start_date, end_date)
    ).exclude(status='Cancelled')

    # Prepare appointment data for FullCalendar with color-coding based on status
    calendar_events = [
        {
            'title': f"{appointment.service.name} ({appointment.appointment_type})",
            'start': f"{appointment.appointment_date.isoformat()}T{appointment.appointment_time.isoformat()}",
            'color': '#FFCC00' if appointment.status == 'Pending' else '#378006',
        }
        for appointment in appointments
    ]

    return render(request, 'customer/customer_appointment.html', {
        'user_id': user_id, 
        'services': services, 
        'appointments': json.dumps(calendar_events),  # Serialize events for the template
    })
     

@require_POST
@login_required
def book_appointment(request):
    user = request.user
    appointment_date = request.POST.get('date')
    appointment_time = request.POST.get('time')
    service_id = request.POST.get('service_id')
    appointment_type = request.POST.get('appointment_type')

    # Validate required fields
    if not all([appointment_date, appointment_time, service_id, appointment_type]):
        return JsonResponse({'success': False, 'message': 'All fields are required.'})

    # Check for ongoing appointments or unfinished progress
    ongoing_appointments = Appointment.objects.filter(
        user=user,
        status='Confirmed',
        level__lt=4  # Check for appointments that are not at Level 4
    )

    if ongoing_appointments.exists():
        return JsonResponse({
            'success': False,
            'message': 'You already have an ongoing appointment that is not yet completed.'
        })

    try:
        # Ensure the service exists
        service = Service.objects.get(id=service_id)

        # Check for duplicate appointments
        if Appointment.objects.filter(
            user=user,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).exists():
            return JsonResponse({
                'success': False,
                'message': 'You already have an appointment booked at this time.'
            })

        # Create the appointment with default status "Pending"
        appointment = Appointment.objects.create(
            user=user,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            service=service,
            appointment_type=appointment_type,
            status='Pending'  # Set status to "Pending" by default
        )

        return JsonResponse({
            'success': True,
            'message': 'Appointment booked successfully and is awaiting confirmation!',
            'service_name': service.name,
            'appointment_id': appointment.id
        })
    except Service.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Selected service does not exist.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
    

@login_required
def check_ongoing_appointments(request):
    user = request.user

    logger.info(f"Checking ongoing appointments for user: {user}")

    try:
        # Check if the user has any confirmed appointments that are not yet at level 4
        has_ongoing_appointment = Appointment.objects.filter(
            user=user,
            status='Confirmed',
            level__lt=4  # Assuming 'level' tracks appointment progress
        ).exists()

        logger.info(f"Ongoing appointments found: {has_ongoing_appointment}")
        return JsonResponse({'has_ongoing_appointment': has_ongoing_appointment})
    except Exception as e:
        logger.error(f"Error checking ongoing appointments: {str(e)}")
        return JsonResponse({'error': 'Server error occurred.'}, status=500)

def customer_team_list(request):
    # Fetch therapists with their assigned therapies (services)
    therapists = User.objects.filter(is_therapist=True).prefetch_related('assigned_services')
    
    # Fetch educators along with their subjects
    educators = User.objects.filter(is_educator=True)

    context = {
        'therapists': therapists,
        'educators': educators,
    }
    
    return render(request, 'customer/customer_team.html', context)

def customer_progress_reports(request, user_id):
   
    return render(request, 'customer/customer_progress_reports.html')


def submit_assessment(request, enrollment_id):
    if request.method == "POST":
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        progress_details = request.POST.get("progress_details")
        notes = request.POST.get("notes", "")
        outcome = request.POST.get("outcome")

        # Save the assessment as a Progress entry
        Progress.objects.create(
            enrollment=enrollment,
            report_date=timezone.now(),
            progress_details=progress_details,
            notes=notes,
            outcome=outcome,
        )

        messages.success(request, "Assessment submitted successfully.")
        return redirect("enrollment-list")  # Redirect to the relevant page

    messages.error(request, "Invalid request method.")
    return redirect("enrollment-list")


def process_payment(request):
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        sender_name = request.POST.get('sender_name')
        receiver_name = request.POST.get('receiver_name')
        reference_number = request.POST.get('reference_number')
        payment_amount = request.POST.get('payment_amount')
        receipt = request.FILES.get('receipt')

        # Validate the required fields
        if not all([enrollment_id, sender_name, receiver_name, reference_number, payment_amount, receipt]):
            messages.error(request, "All fields are required to process payment.")
            return redirect('enrollment', user_id=request.user.id)

        try:
            enrollment = get_object_or_404(Enrollment, id=enrollment_id)

            # Create and save the payment record
            payment = Payment.objects.create(
                enrollment=enrollment,
                sender_name=sender_name,
                receiver_name=receiver_name,
                reference_number=reference_number,
                amount=payment_amount,
                receipt=receipt,
                payment_status='Pending'  # Default status
            )
            messages.success(request, "Payment submitted successfully! Awaiting confirmation.")
            return redirect('enrollment', user_id=request.user.id)
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect('enrollment', user_id=request.user.id)
    
#EDUCATOR FUNCTIONS
#EDUCATOR FUNCTIONS
#EDUCATOR FUNCTIONS
#EDUCATOR FUNCTIONS

@login_required
def educator(request, user_id):
    # Fetch the User and Educator objects
    user = get_object_or_404(User, id=user_id)
    educator = get_object_or_404(Educator, user=user)

    if request.method == 'POST':
        # Update User details
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.contact_info = request.POST.get('num', user.contact_info).strip()
        user.address = request.POST.get('address', user.address).strip()

        if request.FILES.get('profile_picture'):
            # Validate and update profile picture
            user.profile_picture = request.FILES['profile_picture']

        # Validate and parse birthday if provided
        birthday = request.POST.get('birthday', user.birthdate)
        if birthday:
            try:
                user.birthdate = datetime.strptime(birthday, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid birthday format. Use YYYY-MM-DD.")

        user.save()

        # Update Educator-specific fields if necessary (e.g., subject)
        educator.subject = request.POST.get('subject', educator.subject).strip()
        educator.save()

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('educator', user_id=user.id)

    return render(request, 'educator/educator.html', {'user': user, 'educator': educator})


@login_required
def educator_profile(request):
    # Get the educator object for the logged-in user
    try:
        user = request.user
        educator = user.educator  # Get the related Educator object
    except AttributeError:
        # If the user is not an educator, redirect or handle the error
        return render(request, 'error_page.html', {'message': 'User is not an educator.'})

    # Fetch schedules for the educator
    schedules = Schedule.objects.filter(educator_id=educator).prefetch_related('enrollment_set__client')

    # Serialize the schedules and related data
    schedules_data = [
        {
            "id": schedule.id,
            "service_name": schedule.service.name,
            "day": schedule.day,
            "time_start": schedule.time_start,
            "time_end": schedule.time_end,
            "educator": {
                "first_name": schedule.educator.user.first_name,
                "last_name": schedule.educator.user.last_name
            },
            "enrollments": [
                {
                    "client_first_name": enrollment.client.first_name,
                    "client_last_name": enrollment.client.last_name
                }
                for enrollment in schedule.enrollment_set.all()
            ]
        }
        for schedule in schedules
    ]

    # Pass both user and schedules to the template
    return render(request, 'educator/educator_profile.html', {
        'user': user,  # User object to access details like address, contact_info, etc.
        'educator': educator,  # Educator object for specific educator attributes
        'schedules': schedules,
        'schedules_data_json': json.dumps(schedules_data)  # Pass JSON-encoded data to the template
    })

def educator_classes(request):
    user_educator = request.user.educator
    schedules = Schedule.objects.filter(educator_id=user_educator) 
    return render(request, 'educator/educator_profile.html', {'schedules': schedules})

def educator_students(request):
    # Fetch the educator linked to the logged-in user
    educator = get_object_or_404(Educator, user=request.user)
    
    # Fetch only enrollments with status "Enrolled" for this educator
    enrolled_students = Enrollment.objects.filter(educator=educator, status='Enrolled').select_related('client', 'schedule')

    return render(request, 'educator/educator_students.html', {
        'enrolled_students': enrolled_students,
    })


def add_resources(request):
    if request.method == 'POST':
        resource_name = request.POST.get('resource_name')
        resource_type = request.POST.get('resource_type')
        availability = request.POST.get('availability') == 'True'

        new_resource = Resources(
            resource_name=resource_name,
            resource_type=resource_type,
            availability=availability
        )
        new_resource.save()
        return redirect('educator')

    return render(request, 'educator/add_resources.html')

def educator_classes(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    resources = Resources.objects.filter(schedule=schedule)

    if request.method == 'POST':
        # Retrieve form data directly from the request
        resource_name = request.POST.get('resource_name')
        resource_type = request.POST.get('resource_type')
        description = request.POST.get('description')
        availability = request.POST.get('availability') == 'on'
        file = request.FILES.get('file')

        # Create and save the new resource
        new_resource = Resources(
            resource_name=resource_name,
            resource_type=resource_type,
            description=description,
            availability=availability,
            schedule=schedule
        )
        
        # Save the file if provided
        if file:
            new_resource.file = file
        new_resource.save()
        
        return redirect('educator_classes', schedule_id=schedule_id)

    context = {
        'class_info': schedule,
        'resources': resources,
    }
    return render(request, 'educator/educator_classes.html', context)

def educator_schedule_view(request):
  
    schedules = Schedule.objects.all().prefetch_related('enrollment_set__client')
    return render(request, 'educator_schedule.html', {'schedules': schedules})

def edit_resource(request, class_id):
    if request.method == "POST":
        resource_id = request.POST.get("resource_id")
        resource = get_object_or_404(Resources, id=resource_id)

        # Update resource fields
        resource.resource_name = request.POST.get("resource_name")
        resource.resource_type = request.POST.get("resource_type")
        resource.description = request.POST.get("description")
        resource.availability = "availability" in request.POST  # Checkbox handling

        # Handle file upload
        if "file" in request.FILES:
            resource.file = request.FILES["file"]

        resource.save()
        messages.success(request, "Resource updated successfully.")
        
    return redirect("educator_classes", class_id=class_id)

def save_progress(request): 
    if request.method == 'POST': 
        progress = request.POST.get('progress') 
        notes = request.POST.get('notes') 
        outcome = request.POST.get('outcome') 
        new_progress = Progress(progress=progress, notes=notes, outcome=outcome) 
        new_progress.save() 
        return JsonResponse({'success': True, 'message': 'Progress saved successfully!'}) 
    return JsonResponse({'success': False, 'message': 'Failed to save progress.'})

@login_required
def therapist_profile(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        # Update User fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.address = request.POST.get('address', user.address)
        user.contact_info = request.POST.get('contact_info', user.contact_info)

        # Handle and save birthdate
        birthdate = request.POST.get('birthdate')
        if birthdate:
            user.birthdate = birthdate

        # Update profile picture if uploaded
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        try:
            user.save()  # Save the updated user
            messages.success(request, 'Your profile has been updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating profile: {e}')
        
        return redirect('therapist_profile')

    return render(request, 'therapist/therapist.html', {'user': user})


def update_therapist_progress(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        therapist = request.user

        if not therapist.is_therapist:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        # Check if a progress record already exists for the appointment
        progress, created = therapist_Progress.objects.get_or_create(
            appointment=appointment,
            defaults={
                'progress': 0,
                'notes': '',
                'outcome': '',
                'finish_session': "Unfinished",
            }
        )

        # Update progress details
        progress.progress = request.POST.get('progress', progress.progress)
        progress.notes = request.POST.get('notes', progress.notes)
        progress.outcome = request.POST.get('outcome', progress.outcome)
        progress.finish_session = "Finished"
        progress.save()

        return JsonResponse({
            'message': 'Progress updated successfully.',
            'created': created  # True if new record was created, False otherwise
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    progress_entries = therapist_Progress.objects.filter(appointment=appointment)

    total_progress = sum(entry.progress for entry in progress_entries) // len(progress_entries) if progress_entries else 0

    return JsonResponse({
        'appointment': {
            'user': f"{appointment.user.first_name} {appointment.user.last_name}",
            'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d'),
            'appointment_time': appointment.appointment_time.strftime('%H:%M:%S'),
            'appointment_type': appointment.get_appointment_type_display(),
            'status': appointment.get_status_display(),
            'service': appointment.service.name,
        },
        'progress': [
            {
                'progress': entry.progress,
                'notes': entry.notes,
                'outcome': entry.outcome,
                'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for entry in progress_entries
        ],
        'total_progress': total_progress,  # Send total progress as average
    })
@login_required
def therapist_appointments(request):
    therapist = request.user

    if not therapist.is_therapist:
        return redirect('index')

    # Fetch all appointments for the logged-in therapist
    appointments = Appointment.objects.filter(
        therapist=therapist
    ).order_by('appointment_date', 'appointment_time')

    return render(request, 'therapist/therapist_appointments.html', {
        'appointments': appointments,
    })

def therapist_progress(request):
    if not request.user.is_authenticated or not request.user.is_therapist:
        return redirect('login')

    # Fetch customers with finished therapy sessions
    customers = User.objects.filter(
        is_client=True,
        appointment__service__assigned_therapist=request.user,
        appointment__status='Confirmed',
        appointment__progress_entries__finish_session="Finished"
    ).distinct().annotate(
        total_progress=Sum('appointment__progress_entries__progress')
    )

    return render(request, 'Therapist/therapist_progress.html', {
        'customers': customers,
    })


def customer_progress_details(request, customer_id):
    if not request.user.is_authenticated or not request.user.is_therapist:
        return JsonResponse({'success': False, 'message': 'Unauthorized access'}, status=403)

    try:
        customer = User.objects.get(id=customer_id, is_client=True)
        progress_entries = therapist_Progress.objects.filter(
            appointment__user=customer,
            appointment__service__assigned_therapist=request.user,
            finish_session="Finished"
        ).values(
            'appointment__service__name', 'progress', 'notes', 'outcome', 'timestamp'
        )

        total_progress = progress_entries.aggregate(Sum('progress'))['progress__sum'] or 0
        return JsonResponse({
            'success': True,
            'customer_name': f'{customer.first_name} {customer.last_name}',
            'total_progress': total_progress,
            'progress_entries': list(progress_entries),
        })

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Customer not found'}, status=404)
    


def get_pending_appointments_count(request):
    pending_count = Appointment.objects.filter(status='Pending').count()
    return JsonResponse({"pending_appointments_count": pending_count})

def get_pending_enrollments_count(request):
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()
    return JsonResponse({"pending_enrollments_count": pending_enrollments_count})


def assign_therapist_to_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        therapist_id = request.POST.get('therapist_id')

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            therapist = User.objects.get(id=therapist_id, is_therapist=True)
            
            # Assign the therapist
            appointment.therapist = therapist
            appointment.status = 'Confirmed'  # Optionally update status to 'Confirmed'
            appointment.save()

            messages.success(request, "Therapist assigned successfully.")
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
        except User.DoesNotExist:
            messages.error(request, "Therapist not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return redirect('admin_appointments') 


@login_required
def update_appointment_level(request, appointment_id):
    if not request.user.is_therapist:
        return HttpResponseForbidden("You are not authorized to perform this action.")

    # Ensure the therapist is updating their own appointments
    appointment = get_object_or_404(Appointment, id=appointment_id, therapist=request.user)

    if request.method == "POST":
        new_level = request.POST.get('level')
        # Allow levels from 0 to 4
        if new_level and new_level.isdigit() and 0 <= int(new_level) <= 4:
            appointment.level = int(new_level)
            appointment.save()
        return redirect('therapist_appointments')
    
@login_required
def therapist_add_progress(request, appointment_id):
    if not request.user.is_therapist:
        return HttpResponseForbidden("You are not authorized to perform this action.")

    appointment = get_object_or_404(Appointment, id=appointment_id, therapist=request.user)

    if request.method == "POST":
        notes = request.POST.get("notes")
        outcome = request.POST.get("outcome")
        progress_details = request.POST.get("progress_details")

        if notes and outcome and progress_details:
            Progress.objects.create(
                appointment=appointment,
                progress_details=progress_details,
                notes=notes,
                outcome=outcome,
                report_date=now().date()
            )
            messages.success(request, "Progress added successfully.")
        else:
            messages.error(request, "Please fill in all fields.")

        return redirect('therapist_appointments')
    
@require_POST
@login_required
def toggle_schedule_status(request, schedule_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to perform this action.")

    schedule = get_object_or_404(Schedule, id=schedule_id)

    # Toggle the status
    if schedule.status == Schedule.OPEN:
        schedule.status = Schedule.CLOSED
    else:
        schedule.status = Schedule.OPEN

    schedule.save()

    messages.success(request, f"Schedule status has been changed to {schedule.status}.")
    return redirect('admin_schedule')  # Update with the correct URL name 


@login_required
def admin_chat_page(request):
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    pending_enrollments_count = Enrollment.objects.filter(status='Pending').count()

    # Filter users: not staff, not therapists, not educators, and have enrollments or appointments
    users = User.objects.filter(
    is_staff=False,  # Exclude admin users
    is_therapist=False,  # Exclude therapists
    is_educator=False,  # Exclude educators
    is_client=True  # Include only client users
)

    context = {
        'users': users,
        'pending_enrollments_count': pending_enrollments_count,
        'pending_appointments_count': pending_appointments_count,
    }
    return render(request, 'Admin/admin_chatbox.html', context)

@login_required
def fetch_chat_messages(request, user_id):
    last_message_id = request.GET.get('last_message_id', None)
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    messages_query = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    )

    if last_message_id:
        messages_query = messages_query.filter(id__gt=last_message_id)

    messages_data = list(messages_query.values(
        'id',
        'sender__id',
        'sender__username',
        'message',
        'timestamp'
    ).order_by('timestamp'))

    for message in messages_data:
        message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        message['sender_is_client'] = not User.objects.get(id=message['sender__id']).is_staff

    return JsonResponse({'messages': messages_data})


@csrf_exempt
@login_required
def send_chat_message(request):
    """Send a chat message."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            receiver_id = data.get('receiver_id')
            message_content = data.get('message')

            if not receiver_id or not message_content:
                return JsonResponse({'success': False, 'error': 'Receiver and message are required.'}, status=400)

            receiver = User.objects.filter(id=receiver_id).first()
            if not receiver:
                return JsonResponse({'success': False, 'error': 'Receiver not found.'}, status=404)

            message = ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message_content
            )

            # Return the message directly
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'sender_id': message.sender.id,
                    'sender_username': message.sender.username,
                    'message': message.message,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

