from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.views.generic import RedirectView

urlpatterns = [
    # OpenAPI schema
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # App v1
    path("api/v1/", include("core.urls")),

    # Redireciona a raiz ("/") para o Swagger
    path("", RedirectView.as_view(url="/api/v1/schema/swagger-ui/", permanent=False)),
]
