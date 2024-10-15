from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("hello", views.hello),

    path("add_cache_test", views.add_cache_test),
    path("get_cache_test", views.get_cache_test),
    path("test_update_conversations_limits", views.test_update_conversations_limits),
    path("test_save_conversation_limit_data", views.test_save_conversation_limit_data),
    path("delete_all_cache_test", views.delete_all_cache_test),
    
    path("sefremit_verification", views.sefremit_verification),
    path("create_event", views.create_event),
    path("add_event_images", views.add_event_images),
    path('images/<str:category>/<str:filename>/', views.other_images, name='other_images'),
    path('images/<str:category>/<str:promotion>/<str:filename>/', views.catalog_images, name='catalog_images'),
    path('pdf/<str:filename>/', views.serve_pdf, name='serve_pdf'),


    path("upload_daily_rates_image", views.upload_daily_rates_image),
    path("upload_events_image", views.upload_events_image),
    path("upload_promotions_image", views.upload_promotions_image),
    path("remove_events_image", views.remove_events_image),
    path("remove_promotions_image", views.remove_promotions_image)

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

