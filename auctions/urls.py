from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:item_id>', views.item, name='item'),
    path('create', views.create, name='create'),
    path('<int:item_id>/place_bid', views.place_bid, name='place_bid'),
    path('<int:item_id>/post_comment', views.post_comment, name='post_comment'),
    path('<int:item_id>/close_listing', views.close_listing, name='close_listing'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('watchlist_add/<int:item_id>', views.watchlist_add, name='watchlist_add'),
    path('watchlist_remove/<int:item_id>', views.watchlist_remove, name='watchlist_remove'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category>', views.category, name='category'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
]
