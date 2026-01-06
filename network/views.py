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
        return render(request, "network/index.html", {
            'page_obj' : page_obj,
            'postForm' : createPostForm()
        })
    

def post_list(request):
    all_posts = Post.objects.all().order_by('-timestamp')
    p = Paginator(all_posts, 10)
    n = request.GET.get('page')
    pages = p.page(n).object_list()
    return render(request, 'network/pages.html', {
        'pages' : pages
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
    })


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
