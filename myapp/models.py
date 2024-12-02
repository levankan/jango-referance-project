from django.db import models

class ChoiceRecord(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-generated primary key
    random_id = models.IntegerField()
    selected_option = models.CharField(max_length=255)

    def __str__(self):
        return f"Record {self.id} - {self.selected_option}"


class ContactInfo(models.Model):
    email_area = models.EmailField()
    text_area = models.TextField()

    def __str__(self):
        return f"Record {self.email_area} - {self.text_area}"