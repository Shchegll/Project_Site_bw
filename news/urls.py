# news/urls
from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path("", views.NewsListView.as_view(), name="news_page"),
    # path('', views.news_list, name='news_page'),
    # path('debug/', views.debug_news, name='debug_news'),  # для отладки
    # path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path("create/", views.NewsCreateView.as_view(), name="create"),
    path("<int:pk>/", views.NewsDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.NewsUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.NewsDeleteView.as_view(), name="delete"),
]
