from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name= 'index'),
    path('login/', views.login_view, name='login_view'),
    path('signup/', views.signup, name='signup'),
    path('employee/', views.employee, name='employee'),
    path('adminpage/', views.admin, name='adminpage'),
    path('logout/', views.logout_view, name='logout'),

      
    path('admin_services/', views.admin_services, name='admin_services'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_service/', views.add_service, name='add_service'),
    path('update_service/<int:service_id>/', views.update_service, name='update_service'),
    path('delete_service/<int:service_id>/', views.delete_service, name='delete_service'),
    path('delete-enrollment/<int:enrollment_id>/', views.delete_enrollment, name='delete_enrollment'),
    path('pending-appointments-count/', views.get_pending_appointments_count, name='pending_appointments_count'),
    path('pending-enrollments-count/', views.get_pending_enrollments_count, name='pending_enrollments_count'),

    path('user_list/', views.user_list, name='user_list'),  
    path('add_user/', views.add_user, name='add_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),

    path('admin_schedule/', views.admin_schedule, name='admin_schedule'),
    path('add_schedule/', views.add_schedule, name='add_schedule'), 
    path('edit_schedule/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('delete_schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('enrollments/', views.enrollment_list_view, name='enrollment-list'),
    path('all_appointments/', views.admin_display_appointments, name='admin_appointments'),
    path('update_appointment_status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    path('delete_appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('admin_services/<int:service_id>/assign-therapist/', views.assign_therapist, name='assign_therapist'),
    path('admin_payments/', views.admin_payments_view, name='admin_payments'),
    path('assign-therapist/', views.assign_therapist_to_appointment, name='assign_therapist_to_appointment'),
    path('toggle_schedule_status/<int:schedule_id>/', views.toggle_schedule_status, name='toggle_schedule_status'),
    path('admin_chatbox/', views.admin_chat_page, name='admin_chatbox'),
    path('chat/messages/<int:user_id>/', views.fetch_chat_messages, name='fetch_chat_messages'),
    path('chat/send/', views.send_chat_message, name='send_chat_message'),

    
   

  
## USER
## USER

    path('customer/<int:user_id>/', views.customer, name='customer'),
    path('customer_appointment/<int:user_id>/', views.customer_appointment, name='customer_appointment'),
    path('enrollment/<int:user_id>/', views.enrollment_view, name='enrollment'),
    path('customer_therapy/<int:user_id>/', views.customer_therapy, name='customer_therapy'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('team_list/', views.customer_team_list, name='team_list'),
    path('progress_reports/<int:user_id>/', views.customer_progress_reports, name='progress_reports'),
    path('submit-assessment/<int:enrollment_id>/', views.submit_assessment, name='submit_assessment'),
    path('customer_class/<int:user_id>/', views.customer_classes, name='customer_class'),
    path('class_resources/<int:schedule_id>/', views.class_resources, name='class_resources'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('cancel_enrollment/<int:enrollment_id>/', views.cancel_enrollment, name='cancel_enrollment'),

# EDUCATOR    
# EDUCATOR    

    path('educator/<int:user_id>/', views.educator, name='educator'),
    path('educator_profile/', views.educator_profile, name='educator_profile'),
    path('classes/<int:schedule_id>/', views.educator_classes, name='educator_classes'),
    path('add_resources/', views.add_resources, name='add_resources'),
    path('educator_students/', views.educator_students, name='educator_students'),
    path('edit_resource/<int:class_id>/', views.edit_resource, name='edit_resource'),
   

    
## THERAPIST
    path('therapist/', views.therapist_profile, name='therapist_profile'),
    path('therapist_appointments/', views.therapist_appointments, name='therapist_appointments'),
    path('update-progress/<int:appointment_id>/', views.update_therapist_progress, name='update_progress'),
    path('appointment-details/<int:appointment_id>/', views.appointment_details, name='appointment_details'),
    path('therapist_progress/', views.therapist_progress, name='therapist_progress'),
    path('therapist/customer-progress/<int:customer_id>/', views.customer_progress_details, name='customer-progress-details'),
    path('therapist/update_appointment_level/<int:appointment_id>/', views.update_appointment_level, name='update_appointment_level'),
    path('therapist/add-progress/<int:appointment_id>/', views.therapist_add_progress, name='add_progress'),
    path('customer/check-ongoing-appointments/', views.check_ongoing_appointments, name='check_ongoing_appointments'),
    
]