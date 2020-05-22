from django.urls import path, include
from user.views import user_logout


urlpatterns = [
    path('logout/', user_logout, name="logout"),
]