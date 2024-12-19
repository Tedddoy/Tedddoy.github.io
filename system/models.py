from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.timezone import now


class User(AbstractUser):
    is_admin= models.BooleanField('Is admin', default=False)
    is_client = models.BooleanField('Is client', default=False)
    is_employee = models.BooleanField('Is employee', default=False)
    is_therapist = models.BooleanField('Is therapist', default=False)
    is_educator = models.BooleanField('Is educator', default=False)
    birthdate = models.DateField(null=True, blank=True)  
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    contact_info = models.CharField(null=True, max_length=255)  # Move here
    address = models.CharField(null=True, max_length=255)
    specialization = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    
    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        else:
           return '/static/images/default-profile.png'
        
    def __str__(self):
        return self.username
    

class Category(models.Model):
    category = models.CharField(null=True, max_length=255)

    def __str__(self):
        return self.category

class Service(models.Model):
    category_id = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(null=True,)
    availability = models.BooleanField(null=True, default=True)
    assigned_therapist = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={'is_therapist': True},
        related_name='assigned_services'
    )  # New field for therapist assignment

    def __str__(self):
        return self.name
    
    @property
    def availability_text(self):
        return "Yes" if self.availability else "No"
    
class Therapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    specialization = models.CharField(null=True, max_length=255)
 

    def __str__(self):
        return f"{self.user.username}"  

class Educator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField(null=True, max_length=255)


    def __str__(self):
        return f"{self.user.username}"


class Schedule(models.Model):
    OPEN = 'Open'
    CLOSED = 'Closed'

    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
    ]
    educator = models.ForeignKey(Educator, null=True, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, null=True, on_delete=models.CASCADE)  # Renamed to `service`
    day = models.CharField(null=True, max_length=10)
    time_start = models.CharField(null=True, max_length=10)
    time_end = models.CharField(null=True, max_length=10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)

    def __str__(self):
         return f"{self.day} {self.time_start} - {self.time_end} ({self.status})"



class Appointment(models.Model):
    APPOINTMENT_TYPE_CHOICES = [
        ('in-house', 'In-house'),
        ('walk-in', 'Walk-in'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    LEVEL_CHOICES = [
        (0, 'Level 0 - 0%'),
        (1, 'Level 1 - 25%'),
        (2, 'Level 2 - 50%'),   
        (3, 'Level 3 - 75%'),
        (4, 'Level 4 - 100%'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', limit_choices_to={'is_therapist': True}, null=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE_CHOICES, default='walk-in')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1)

    def get_progress(self):
        """Calculate the progress percentage based on the level."""
        return self.level * 25

    def __str__(self):
        return f'Appointment for {self.user.username} on {self.appointment_date} at {self.appointment_time}, Type: {self.appointment_type}, Status: {self.status}, Level: {self.level}, Progress: {self.get_progress()}%'

class Resources(models.Model):
    RESOURCE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
    ]
    resource_name = models.CharField(null=True, max_length=255)
    resource_type = models.CharField(null=True, max_length=10, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='resources/files/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    availability = models.BooleanField(null=True, default=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='resources', null=True)
    educator = models.ForeignKey(Educator, null=True, on_delete=models.CASCADE, related_name='resources')
    
    def __str__(self):
        return self.resource_name
    

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Canceled', 'Canceled'),
    ]
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    educator = models.ForeignKey(Educator, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.client.username} enrolled in {self.schedule.service.name} with {self.educator.user.username}"
    

class Progress(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, related_name="progress_notes")  
    report_date = models.DateField(auto_now_add=True, null=True) 
    progress_details = models.TextField(null=True) 
    notes = models.TextField(blank=True, null=True)  
    outcome = models.CharField(max_length=255, null=True)  

    def __str__(self):
        return f"Progress Report for Appointment {self.appointment} on {self.report_date}"

class Assessment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)  
    total_month = models.PositiveIntegerField()  
    sub_amount = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"Assessment for Enrollment {self.enrollment.id} - Total Months: {self.total_month}, Sub Amount: {self.sub_amount}"
    
class OfficialReceipt(models.Model):
    sender_name = models.CharField(max_length=255) 
    service = models.ForeignKey(Service, on_delete=models.CASCADE) 
    service_price = models.DecimalField(max_digits=10, decimal_places=2)  
    enrollment_duration = models.PositiveIntegerField() 
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  
    reference_number = models.CharField(max_length=255, unique=True)  
    generated_date = models.DateTimeField(auto_now_add=True)  

    def save(self, *args, **kwargs):
        """Automatically calculate total_price before saving."""
        if self.service_price and self.enrollment_duration:
            self.total_price = self.service_price * self.enrollment_duration
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt {self.reference_number} for {self.sender_name}"
    

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    CONFIRMATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
    ]
    
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE, null=True, blank=True)  # Link to Enrollment
    sender_name = models.CharField(max_length=255, null=True, blank=True)  # Name of the depositor
    receiver_name = models.CharField(max_length=255, null=True, blank=True)  # Name of the receiver
    reference_number = models.CharField(max_length=255, null=True, blank=True)  # Reference number of the transaction
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Payment amount
    receipt = models.ImageField(upload_to='payment_receipts/', null=True, blank=True)  # Uploaded receipt
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Confirmed')
    confirmation_status = models.CharField(max_length=20, choices=CONFIRMATION_STATUS_CHOICES, default='Confirmed')
    payment_date = models.DateTimeField(auto_now_add=True)  # Date when payment was made

    def __str__(self):
        return f"Payment {self.id} - {self.payment_status}"

    
class Invoice(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)  # Link to the Appointment model
    total_hour = models.PositiveIntegerField()  # Assuming total hours is a positive integer
    sub_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Decimal for subtotal amount

    def __str__(self):
        return f"Invoice {self.id} for Appointment {self.appointment.id} - Total Hours: {self.total_hour}, Sub Amount: {self.sub_amount}"
    

class therapist_Progress(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='progress_entries'
    )
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    progress = models.IntegerField(default=0, null=True)
    notes = models.CharField(max_length=255, null=True)
    outcome = models.CharField(max_length=255, null=True)
    finish_session = models.CharField(max_length=255, default="Unfinished")

    def __str__(self):
        return f"Progress for {self.appointment} at {self.timestamp}"
    
User = get_user_model()

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"
