import json
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Site
    path('admin/', admin.site.urls),
    
    # INCLUDE the explorer app URLs at the project root ('')
    # This directs requests for /, /api/execute/, /api/save/, etc., to the explorer app.
    path('', include('explorer.urls')), 
]
