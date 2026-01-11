from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("hello", views.hello),
    path("verification", views.verification),
    path("get_shelve_talker_by_barcode", views.get_shelve_talker_by_barcode),

]


