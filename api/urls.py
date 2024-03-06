from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from api.views import ProductViewSet, CreateTokenView

router = routers.DefaultRouter()
router.register(r"products", ProductViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("login/", CreateTokenView.as_view(), name="login")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "api"
