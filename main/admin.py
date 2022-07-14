from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Intrare)
admin.site.register(models.Iesire)
admin.site.register(models.Comanda)