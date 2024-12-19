from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Educator)
admin.site.register(Service)
admin.site.register(Category)
admin.site.register(Appointment)
admin.site.register(Enrollment)
admin.site.register(Progress)
admin.site.register(Assessment)
admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(therapist_Progress)
admin.site.register(Therapist)
admin.site.register(ChatMessage)
admin.site.register(Resources)

admin.site.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('service', 'educator', 'day', 'time_start', 'time_end', 'status')
    list_filter = ('status',)
    actions = ['open_schedule', 'close_schedule']

    def open_schedule(self, request, queryset):
        queryset.update(status=Schedule.OPEN)
        self.message_user(request, "Selected schedules have been opened.")

    def close_schedule(self, request, queryset):
        queryset.update(status=Schedule.CLOSED)
        self.message_user(request, "Selected schedules have been closed.")

    open_schedule.short_description = "Mark selected schedules as Open"
    close_schedule.short_description = "Mark selected schedules as Closed"