from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import User,Listing,Bid,Comment


def index(request):
    user_listings = Listing.objects.all
    
    return render(request, "auctions/index.html", {"user_listings": user_listings})

def listing_description(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.all()

    if request.method == 'POST':
        # Process new comment submission
        content = request.POST.get('comment_content')
        if content:
            new_comment = Comment.objects.create(listing=listing, user=request.user, comment=content)
            # Redirect to avoid form resubmission on page refresh
            return HttpResponseRedirect(reverse('listing_description', args=[listing_id]))
    return render(request, 'auctions/listing_description.html', {'listing': listing, 'comments': comments})

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

def user_listing(request):
    user_listings = Listing.objects.filter(seller=request.user)
    return render(request, "auctions/user_listing.html", {"user_listings": user_listings})


def create_listing(request):
    if request.method == "POST":
        # Extract form data
        seller = request.user
        name = request.POST["name"]
        # Check if 'image' key exists in request.FILES
        if 'image' in request.FILES:
            image = request.FILES["image"]
        else:
            image = None
        desc = request.POST["desc"]
        current_highest_bid = request.POST.get("current_highest_bid", 0)

        # Create a new listing object
        new_listing = Listing(
            seller=seller,
            name=name,
            image=image,
            desc=desc,
            current_highest_bid=current_highest_bid
        )
        new_listing.save()

        # Redirect to a success page or display a success message
        return HttpResponseRedirect('user_listing')  # Assuming 'index' is the URL name for the homepage
    else:
        return render(request,"auctions/create_listing.html") 


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
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

def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == 'POST':
        bid_amount_str = request.POST.get('bid_amount')
        try:
            bid_amount = int(bid_amount_str)
        except ValueError:
            messages.error(request, 'Invalid bid amount.')
            return redirect('listing_description', listing_id=listing_id)
        bidder = request.user
        if bidder != listing.seller and bid_amount > listing.current_highest_bid:
            listing.current_highest_bid = bid_amount
            listing.update_current_bid(bidder)
            listing.save()
            Bid.objects.create(listing=listing, bidder=bidder, bid_price=bid_amount)
            messages.success(request, 'Bid placed successfully!')
        else:
            messages.error(request, 'Unable to place bid.')
    return redirect('listing_description', listing_id=listing_id)