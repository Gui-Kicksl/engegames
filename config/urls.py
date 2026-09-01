from django.contrib import admin
from django.urls import include, path

from jogo import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("jogo.urls")),
    path("", views.pagina_do_jogo, name="pagina_do_jogo"),
]
