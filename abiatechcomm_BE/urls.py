from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# drf-spectacular views (modern OpenAPI 3 replacement for drf-yasg)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    path('admin/', admin.site.urls),

    # Your API apps
    path("api/v1/auth/", include("api.urls")),
    path("api2/v1/auth/", include("api2.urls")),
    # path('onboard/', include("onboarding.urls")),  # uncomment when ready

    # JWT authentication endpoints
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API Schema & Documentation (using drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),                  # raw OpenAPI JSON/YAML
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),   # Swagger UI at root "/"
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),    # Redoc UI
]

# Serve media files in development (DEBUG mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)