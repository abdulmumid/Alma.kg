from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'hurry', HurryBuyViewSet, basename='hurry')
router.register(r'stories', StoryViewSet, basename='stories')

urlpatterns = [
    path('stores/nearest/', NearestStoreView.as_view(), name='nearest_store'),
    path('stores/', StoreListView.as_view(), name='store-list'),
    path('', include(router.urls)),
]
