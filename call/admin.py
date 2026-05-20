from django.contrib import admin

# Register your models here.
from .models import User, Staff, Meeting ,PaymentProof

admin.site.register(User)
admin.site.register(Staff)
admin.site.register(Meeting)
admin.site.register(PaymentProof)
