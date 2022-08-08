from django.contrib import admin
from . import models
# Register your models here.

ADMIN_REORDER = (
# 'webapp',

#### First group
{
    'app': 'main',
    'label': 'Date de la angajati',
    'models': (
        'main.Intrare',
        'main.Iesire',
        'main.Comanda',
        'main.Info',
    )
},
# Second group: same app, but different label
{
    'app': 'main',
    'label': 'Utilizatori',
    'models': (
        'main.User',
    )
},
{
    'app': 'main',
    'label': 'Setari',
    'models': (
        'main.Forma',
        'main.OwnSettings',
    )
},
)
admin.site.register(models.Forma)
admin.site.register(models.Harta)
admin.site.register(models.OwnSettings)

admin.site.register(models.User)
admin.site.register(models.Intrare)
admin.site.register(models.Iesire)
admin.site.register(models.Comanda)
admin.site.register(models.Lucru)
admin.site.register(models.Info)