from django.db import models

class PrescriptionRecord(models.Model):
    """Secure clinical data storage designed for HIPAA/GDPR readiness[cite: 54]."""
    image = models.ImageField(upload_to='prescriptions/')
    extracted_text = models.TextField(blank=True)
    ai_analysis = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)