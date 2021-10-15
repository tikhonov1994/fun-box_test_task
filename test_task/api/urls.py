from django.urls import path

from .views import get_domains, save_links

urlpatterns = [
    path('visited_links', save_links),
    path('visited_domains', get_domains),
]
