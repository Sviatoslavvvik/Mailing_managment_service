from api.views import ClientViewset, MailingViewset
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

schema_view = get_schema_view(
   openapi.Info(
      title="Mailing Service API",
      default_version='v1',
      description="Документация для сервиса рассылок",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

api_router = DefaultRouter()
api_router.register(
    'clients', ClientViewset, basename='clients'
)
api_router.register(
    'mailings', MailingViewset, basename='mailings'
)

urlpatterns = [
    path('', include(api_router.urls)),
    path('admin/', admin.site.urls),
]

urlpatterns += [
   url(r'^swagger(?P<format>\.json|\.yaml)$',
       schema_view.without_ui(cache_timeout=0), name='schema-json'),
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
       name='schema-swagger-ui'),
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
       name='schema-redoc'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),) 