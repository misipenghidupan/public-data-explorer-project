from django.urls import path
from . import views

urlpatterns = [
    # Main View: Handles the root URL and loads the index.html template
    path('', views.explorer_view, name='explorer_view'),

    # API Endpoints (Must match the paths used by the JavaScript frontend)
    path('api/execute/', views.execute_query, name='execute_query'),
    path('api/save/', views.save_query, name='save_query'),
    path('api/queries/', views.list_queries, name='list_queries'),
]
