from django.urls import path
from .views import CreateShortURLView, RedirectShortURLView


urlpatterns = [
    path('shorten',  CreateShortURLView.as_view(), name='create_short_url'),
    path('<str:short_code>', RedirectShortURLView.as_view(), name='redirect_short_url'),
]