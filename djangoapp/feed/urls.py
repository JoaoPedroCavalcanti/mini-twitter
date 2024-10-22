from django.urls import path

from feed.views import FeedView

urlpatterns = [
    path('', FeedView.as_view(), name='user-feed')
]

