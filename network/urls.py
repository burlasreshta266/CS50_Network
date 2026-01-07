
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following_page, name="following_page"),
    path("edit_post/<int:id>", views.edit_post, name="edit_post"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("follow/<str:username>", views.follow_user, name="follow_user"),
]
