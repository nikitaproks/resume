from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to="documents/")
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.title
