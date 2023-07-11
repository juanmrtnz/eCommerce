from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from django.core.validators import MinValueValidator
from datetime import datetime
from .models import *

class CreateListingForm(ModelForm, forms.Form):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'price', 'photo', 'category']
        labels = {'photo': "Photo (paste URL):"}
        widgets = {'title': forms.TextInput({'autofocus': 'on'}), 'description': forms.Textarea(attrs={'rows':20, 'cols':50})}
    price = forms.FloatField(label="Starting price ($):", validators=[MinValueValidator(0.01)])

class CommentForm(forms.Form):
    text = forms.CharField(label="", max_length=140, required=False, widget=forms.Textarea(attrs={'rows':4, 'cols':50}))

class BidForm(forms.Form):
    amount = forms.FloatField(label="", required=False)


def index(request):
    return render(request, "auctions/index.html", {
        'items': AuctionListing.objects.all(),
        'bids': Bid.objects.all()
    })


def item(request, item_id):
    return render(request, 'auctions/item.html', {
        'item': AuctionListing.objects.get(pk=item_id),
        'bid': Bid.objects.get(item=AuctionListing.objects.get(pk=item_id)),
        'comments': AuctionComment.objects.filter(item=AuctionListing.objects.get(pk=item_id)),
        'comment_form': CommentForm(),
        'bid_form': BidForm(),
        })


def create(request):
    if request.method == 'POST':
        form = CreateListingForm(request.POST)
        if form.is_valid():
            form_title = form.cleaned_data['title']
            form_description = form.cleaned_data['description']
            form_price = form.cleaned_data['price']
            form_photo = form.cleaned_data['photo']
            form_category = form.cleaned_data['category']
            new_listing = AuctionListing(user=User.objects.get(username=request.user.username), title=form_title, description=form_description, price=form_price, photo=form_photo, category=form_category)
            new_listing.save()
            new_bid = Bid(item=AuctionListing.objects.get(pk=new_listing.id), user=User.objects.get(username=request.user.username), amount=form_price)
            new_bid.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, 'auctions/error_textarea_bug.html')
    
    return render(request, 'auctions/create.html', {
        'form': CreateListingForm()
    })


def place_bid(request, item_id):
    bid_form = BidForm(request.POST)
    if bid_form.is_valid():
        amount = bid_form.cleaned_data['amount']
        current_bid = Bid.objects.get(item=AuctionListing.objects.get(pk=item_id))
        if amount == None or amount < 1 or amount < 0.01 or current_bid.amount > amount:
            return render(request, 'auctions/error_bid.html', {
                'item_id': item_id,
            })
        else:
            AuctionListing.objects.filter(pk=item_id).update(price=amount)
            Bid.objects.filter(item=AuctionListing.objects.get(pk=item_id)).update(user=User.objects.get(username=request.user.username), amount=amount)
            return render(request, 'auctions/success_bid.html', {
                'item_id': item_id,
            })


def post_comment(request, item_id):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            text = comment_form.cleaned_data['text']
        if len(text) < 1:
            return render(request, 'auctions/error_comment.html', {
                'item_id': item_id,
            })
        comment = AuctionComment(item=AuctionListing.objects.get(pk=item_id), user=User.objects.get(username=request.user.username), text=text, timestamp=datetime.now())
        comment.save()

        return render(request, 'auctions/success_comment.html', {
            'item_id': item_id,
        })


def close_listing(request, item_id):
    if request.method == 'POST':
        winner = Bid.objects.get(item=AuctionListing.objects.get(pk=item_id)).user
        AuctionListing.objects.filter(pk=item_id).update(active=False, winner=winner)
        return render(request, 'auctions/success_close.html', {
            'item_id': item_id,
            'winner': winner.username,
        })


def watchlist(request):
    return render(request, 'auctions/watchlist.html', {
        'items': request.user.watchlist.all()
    })


def watchlist_add(request, item_id):
    listing = AuctionListing.objects.get(pk=item_id)
    user = User.objects.get(username=request.user.username)
    user.watchlist.add(listing)
    return HttpResponseRedirect(reverse("watchlist"))


def watchlist_remove(request, item_id):
    listing = AuctionListing.objects.get(pk=item_id)
    user = User.objects.get(username=request.user.username)
    user.watchlist.remove(listing)
    return HttpResponseRedirect(reverse("watchlist"))


def categories(request):
    return render(request, 'auctions/categories.html', {
        'categories': ['Beauty', 'Fashion', 'Health', 'Home', 'Media', 'Sports', 'Other']
        })


def category(request, category):
    return render(request, 'auctions/category.html', {
        'category': category,
        'items': AuctionListing.objects.filter(category=category)
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation and username isn't longer than 10 characters
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        if len(username) > 10:
            return render(request, "auctions/register.html", {
                "message": "Username cannot be longer than 10 characters."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
