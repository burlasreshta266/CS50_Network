import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.urls import reverse
from .models import User, Post, Follow, Like
from .forms import createPostForm


def index(request):
    all_posts = Post.objects.all().order_by('-timestamp')
    p = Paginator(all_posts, 10)

    if request.method=='POST':
        form = createPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        else:
            form = createPostForm()
        return redirect('index')
    else:
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)
        if request.user.is_authenticated:
            for post in page_obj:
                post.is_liked = post.likes.filter(liked_by=request.user).exists()
                post.is_following = post.author.followers.filter(follower=request.user).exists()

        return render(request, "network/index.html", {
            'page_obj' : page_obj,
            'postForm' : createPostForm()
        })
    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def profile(request, id):
    try:
        user = User.objects.get(id=id)
    except:
        return render(request, "network/error.html")
    all_posts = Post.objects.filter(author=user).order_by('timestamp')
    username = user.username
    followers = user.followers.count()
    following = user.following.count()
    p = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    if request.user.is_authenticated:
        for post in page_obj:
            post.is_liked = post.likes.filter(liked_by=request.user).exists()
            post.is_following = post.author.followers.filter(follower=request.user).exists()

    return render(request, "network/profile.html", {
        'page_obj' : page_obj,
        'username' : username,
        'following_count' : following,
        'followers_count' : followers
    })


@login_required
def following_page(request):
    all_posts = Post.objects.filter(author__followers__follower=request.user).order_by("-timestamp")
    p = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    if request.user.is_authenticated:
        for post in page_obj:
            post.is_liked = post.likes.filter(liked_by=request.user).exists()
            post.is_following = post.author.followers.filter(follower=request.user).exists()

    return render(request, "network/following.html", {
        'page_obj' : page_obj,
    })


@login_required
def edit_post(request, id):
    if request.method=='POST':
        data = json.loads(request.body)
        new_content = data.get("edited_content")
        post = Post.objects.get(id=id)
        post.content = new_content
        post.save()
        return JsonResponse({ 'new_content' : new_content })


@login_required
@require_POST
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if post.likes.filter(liked_by=request.user).exists():
        Like.objects.filter(liked_by=request.user, liked_post=post).delete()
        is_like = False
    else:
        Like.objects.create(liked_by=request.user, liked_post=post)
        is_like = True

    return JsonResponse({
        'like_count' : post.likes.count(),
        'is_like' : is_like,
    })


@login_required
@require_POST
def follow_user(request, username):
    following = User.objects.get(username=username)
    follower = request.user
    follow = Follow.objects.filter(follower=follower, following=following)
    if follow.exists():
        follow.delete()
        is_following = False
    else:
        Follow.objects.create(follower=follower, following=following)
        is_following = True
    return JsonResponse({ 'is_following':is_following })    


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
