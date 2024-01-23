from django.contrib import admin
from .models import (
    Company, CompanySettings, UserRole, User, Pipeline, Stage,
    Customer, Affiliate, CustomerNote, AffiliateNote, Notification, EmailTemplate,
)

admin.site.register(Company)
admin.site.register(CompanySettings)
admin.site.register(UserRole)
admin.site.register(User)
admin.site.register(Pipeline)
admin.site.register(Stage)
admin.site.register(Customer)
admin.site.register(Affiliate)
admin.site.register(CustomerNote)
admin.site.register(AffiliateNote)
admin.site.register(Notification)
admin.site.register(EmailTemplate)
