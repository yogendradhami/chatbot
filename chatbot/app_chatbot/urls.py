from django.urls import path
from . import views
urlpatterns =[
    path('',views.Index,name='index'),
    path('specific/', views.Specific,name='specific'),
    # path('article/<int:article_id>/', views.Article,name='article'),
    path('getResponse/',views.getResponse, name='getResponse'),
]