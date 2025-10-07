from django.contrib import admin
from .models import QA

# Custom admin class (optional, for better display)
class QAAdmin(admin.ModelAdmin):
    list_display = ('question',)           # Columns to display in admin list view
    search_fields = ('question', 'answer') # Enable search by question or answer
    list_per_page = 20                     # Pagination in list view

# Register the model with admin site
admin.site.register(QA, QAAdmin)
