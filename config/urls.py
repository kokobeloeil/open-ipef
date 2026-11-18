from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Prépa IPEF — administration"
admin.site.site_title = "Prépa IPEF"
admin.site.index_title = "Gestion du site"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("compte/", include("accounts.urls")),
    path("ressources/", include("ressources.urls")),
    path("faq/", include("faq.urls")),
    path("", include("core.urls")),
]
