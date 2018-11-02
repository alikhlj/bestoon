from django.contrib import admin

# Register your models here.
from .models import Expense
from .models import Income

admin.site.register(Expense)
admin.site.register(Income)