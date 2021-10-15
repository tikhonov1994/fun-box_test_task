from django.urls import path
from .views import save_links, get_domains

urlpatterns = [
    path('visited_links', save_links),
    path('visited_domains', get_domains),
]
