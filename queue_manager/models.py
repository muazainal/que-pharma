import uuid
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

class PharmacistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.employee_id})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # We don't have the employee_id here yet, 
        # but we'll create the shell and update it in the view.
        PharmacistProfile.objects.get_or_create(user=instance)

class PrescriptionTicket(models.Model):
    STATUS_CHOICES = [
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
        ('Collected', 'Collected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tickets')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_tickets')
    queue_number = models.IntegerField(unique=True)
    patient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Preparing')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.queue_number} - {self.patient_name}"
