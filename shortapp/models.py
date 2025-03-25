from django.db import models

from django.utils import timezone
import datetime

class ShortenedURL(models.Model):
    short_code = models.CharField(max_length=6, unique=True)
    original_url = models.URLField(max_length=2048)
    expiration_date = models.DateTimeField()

    def __str__(self):
        return self.short_code
    def is_expired(self):
        return self.expiration_date < datetime.datetime.now(datetime.timezone.utc)
