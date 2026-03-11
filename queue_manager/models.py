"""
Que-Pharma Core Models
Defines the database schema for the Prescription and Pharmacist management systems.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PharmacistProfile(models.Model):
    """
    Extends the default Django User model with specific workplace fields.
    Each Pharmacist is uniquely identified by an Employee ID.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=50, unique=True, help_text="Unique staff identification number")

    def __str__(self):
        return f"{self.user.username} ({self.employee_id})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver: Automatically creates a PharmacistProfile whenever a new User is registered.
    Ensures that every staff member always has a profile shell ready to be populated.
    """
    if created:
        # We don't have the employee_id during the initial User save signal, 
        # so we create the shell here and update it later in the signup view.
        PharmacistProfile.objects.get_or_create(user=instance)

class PrescriptionTicket(models.Model):
    """
    Represents a single patient's prescription in the queue.
    Tracks status from preparation to collection and monitors staff involvement.
    """
    # Standard states for a prescription life cycle
    STATUS_CHOICES = [
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
        ('Collected', 'Collected'),
    ]

    # Use UUID for secure, unguessable tracking URLs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Audit trail: Tracks which pharmacist created and last updated the ticket
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tickets')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_tickets')
    
    # Public identity of the ticket
    queue_number = models.IntegerField(unique=True, help_text="Sequential number displayed to customers")
    patient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="For status notifications via WhatsApp")
    
    # Current status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Preparing')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Latest prescriptions are typically prioritized or shown first in management logs
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.queue_number} - {self.patient_name}"
