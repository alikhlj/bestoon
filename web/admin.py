from django.contrib import admin

# Register your models here.
from .models import Expense
from .models import Income
from .models import Token
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Token)