from django.contrib import admin
from search.models import Dataset

# Register your models here.
class DatasetAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['ID', 'Count']}),
		('Features', 		 {'fields': ['Features']}),
    ]

    list_display = ('ID', 'Count', 'Features')

admin.site.site_header = "Mike' TestSite"
admin.site.register(Dataset, DatasetAdmin)
