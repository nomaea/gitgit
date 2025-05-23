from django.contrib import admin
from .models import UploadedFile, FileLog

admin.site.register(UploadedFile)
admin.site.register(FileLog)
