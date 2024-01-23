from django.db import models
from django.contrib.postgres.fields import ArrayField


class Company(models.Model):
    company_name = models.CharField(max_length=255)
    state_country = models.CharField(max_length=255, null=True, blank=True)
    logo = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.company_name


class CompanySettings(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="settings")
    stage_ids = ArrayField(models.IntegerField(), blank=True, null=True)
    user_roles = ArrayField(models.IntegerField(), blank=True, null=True)
    pipeline_ids = ArrayField(models.IntegerField(), blank=True, null=True)
    workflow_ids = ArrayField(models.IntegerField(), blank=True, null=True)

    def __str__(self):
        return f"Settings - {self.company.company_name}"


class UserRole(models.Model):
    role_name = models.CharField(max_length=255)
    role_id = models.IntegerField(blank=True, null=True)
    role_permissions = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.role_name


class User(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    pipeline_ids = ArrayField(models.IntegerField(), blank=True, null=True)
    token = models.CharField(max_length=254, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.first_name or "No name"


class Pipeline(models.Model):
    pipeline_id = models.IntegerField(blank=True, null=True)
    pipeline_name = models.CharField(max_length=255)

    def __str__(self):
        return self.pipeline_name


class Stage(models.Model):
    stage_name = models.CharField(max_length=255)
    stage_id = models.IntegerField(blank=True, null=True)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)

    def __str__(self):
        return self.stage_name


class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    referral_code = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Affiliate(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=20)
    state = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    external_member_id = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return self.name


class CustomerNote(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=255)
    note_text = models.TextField()
    datetime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.note_title


class AffiliateNote(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=255)
    note_text = models.TextField()

    def __str__(self):
        return self.note_title


class Notification(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    notification_title = models.CharField(max_length=255)
    notification_text = models.TextField()
    generated_datetime = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.notification_title


class EmailTemplate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email_title = models.CharField(max_length=255)
    email_description = models.CharField(max_length=255)
    email_template_image = models.CharField(max_length=255)

    def __str__(self):
        return self.email_title
