from django.urls import path
from .views import DataExplorerView

app_name = 'explorer'

urlpatterns = [
    path('', DataExplorerView.as_view(), name='data_explorer'),
]