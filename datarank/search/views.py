from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys, ast, unicodedata
from search.models import *
from search.Ranking import generalRanking, testRanking
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ipware.ip import get_ip

import time
PAGE_NUM = 20

# Create your views here.
def results(request):
    return render(request, 'search/results.html', {'instruction': 'When you start a search, data would be shown here'})

def index(request):
    return render(request, 'search/index.html')
    
def test(request):
    return render(request, 'search/test.html')

def refresh(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RankForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            data = form.cleaned_data['rank_info']
            print >>sys.stderr, str(data)
            ranks = data.split(',')[:-1]
            rank_string = unicodedata.normalize('NFKD', '{'+','.join(ranks)+'}').encode('ascii', 'ignore')
            rank = ast.literal_eval(rank_string)
            print >>sys.stderr, str(rank)

            if 'ranks' in request.session:
                current = ast.literal_eval(request.session['ranks'])
                for key,value in rank.iteritems():
                    if int(value) == 0:
                        continue;
                    print >>sys.stderr, 'New Rating Updated: '+str(key)+': '+str(value)
                    current[key] = value
                request.session['ranks'] = str(current)
                print >>sys.stderr, 'Updated Session'
                print >>sys.stderr, request.session['ranks']
            else:
                print >>sys.stderr, 'New Session Created'
                current = {}
                for key,value in rank.iteritems():
                    if int(value) == 0:
                        continue
                    print >>sys.stderr, 'New Rating Updated: '+str(key)+': '+str(value)
                    current[key] = value
                if len(current.values()):
                    request.session['ranks'] = str(current)
    if not 'ranks' in request.session:
        print >>sys.stderr, 'No ranks in session'
        return search(request)

    if 'keywords' in request.session:
        print >>sys.stderr, 'keywords Processing Part'
        base_tuples = generalRanking(request.session['keywords'])
        if base_tuples is None:
            return HttpResponseRedirect(reverse('ds:index'))
        rs, base, glist, jraw = zip(*base_tuples)
        if base is None:
            return HttpResponseRedirect(reverse('ds:index'))
        ratings_lists = testRanking(rs, base, request.session['ranks'])

        context = {'lists_top': ratings_lists, 'instruction':'nothing', 'keyword':request.session['keywords']}

        paginator = Paginator(ratings_lists, PAGE_NUM) # Show 25 contacts per page
        page = request.GET.get('page')
        try:
            ratings_lists = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            ratings_lists = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            ratings_lists = paginator.page(paginator.num_pages)

        context = {'lists_top': ratings_lists, 'instruction':'nothing', 'keyword':request.session['keywords']}

        saveRatings(request)
        return render(request, 'search/results.html', context)
    print >>sys.stderr, 'Invalid: redirect to search'
    return HttpResponseRedirect(reverse('ds:search'))

def getUsername(request):
    if request.user.is_authenticated():
        return request.user.username
    else:
        ip = get_ip(request)
        if ip is not None:
            return str(ip)
        else:
            return 'DBMI-UNKNOWN-USER'
    return

def getFileName(rate):
    return rate.username+'_'.join(rate.sessioncreated.split(','))
def saveRatings(request):
    print >>sys.stderr, 'Saving User Ratings'
    rate = SearchRate()
    rate.username = getUsername(request)
    rate.keywords = request.session['keywords']
    rate.ratings = request.session['ranks']
    rate.sessioncreated = request.session['created']
    rate.save()
    return



def search(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        if 'ranks' in request.session:
            del request.session['ranks']

        # check whether it's valid:
        if form.is_valid():
            words = form.cleaned_data['search_words']
            request.session['keywords'] = words
            request.session['created'] = time.strftime("%d,%m,%Y,%H,%M,%S")

    if 'keywords' in request.session:
        base_tuples = generalRanking(request.session['keywords'])
        if base_tuples is None:
            return HttpResponseRedirect(reverse('ds:index'))
        rs, lists, glist, graw = zip(*base_tuples)
        if lists is not None:
            ratings = [0] * len(lists)
            ratings_lists = zip(ratings, lists, rs, glist, graw)

            paginator = Paginator(ratings_lists, PAGE_NUM) # Show 25 contacts per page
            page = request.GET.get('page')
            try:
                ratings_lists = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                ratings_lists = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                ratings_lists = paginator.page(paginator.num_pages)

            context = {'lists_top': ratings_lists, 'instruction':'nothing', 'keyword':request.session['keywords']}
            return render(request, 'search/results.html', context)
        else:
            del request.session['keywords']
            del request.session['created']
    return HttpResponseRedirect(reverse('ds:index'))

def register(request):
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            return render(request,
                    'search/index.html',
                    {'user_form': user_form, 'registered': registered, 'instructions': user_form.errors})

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    # Render the template depending on the context.
    return render(request,
            'search/index.html',
            {'user_form': user_form, 'registered': registered},
            )

def comment(request):
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        # check whether it's valid:
        print >>sys.stderr, 'New Comment Request.'
        if form.is_valid():
            com = form.save()
            com.user = getUsername(request)
            com.keyword = request.session['keywords']
            print >>sys.stderr, 'Valid Comment'
            print >>sys.stderr, com.user+'\'s comment at '+com.dataset_id+' with keywords: '+com.keyword
            print >>sys.stderr, com.comment
            print >>sys.stderr, 'Timestamp: '+str(com.timestamp)
    return refresh(request)

def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                return render(request,
                    'search/index.html',
                    {'instructions': 'account disabled'})
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return render(request,
                'search/index.html',
                {'instructions': 'Invalid login details'})

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'search/login.html')

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')
