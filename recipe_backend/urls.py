"""
URL configuration for recipe_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from recipes.views.viewsets import GoogleLogin
from recipes.views.auth_views import UserDetailView
from recipes.views.stats_views import UserStatisticsView
from recipes.views.shopping_list_views import ShoppingListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("recipes.urls")),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "auth/google/login/callback/",
        GoogleLogin.as_view(),
        name="google_login_callback",
    ),
    path("accounts/", include("allauth.urls")),
    path("user/details/", UserDetailView.as_view(), name="user-details"),
    path("user/statistics/", UserStatisticsView.as_view(), name="user-statistics"),
    path("shopping-list/", ShoppingListView.as_view(), name="shopping-list"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
