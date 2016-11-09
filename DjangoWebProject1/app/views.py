"""
Definition of views.
"""
from datetime import datetime
from datetime import timedelta
from datetime import date
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.template import RequestContext
from .forms import RegisterUserForm
from .forms import RegisterToolForm
from .forms import UpdateToolsForm
from .forms import ShedCreation
from .forms import SearchToolForm
from .forms import BorrowRequestForm
from .forms import UpdatePersonalInfoForm
from .forms import UpdatePersonalInfoForm2
from .forms import UpdateUserProfileForm
from .forms import UpdateUserProfileForm2
from .forms import UpdateShareZoneForm2
from .forms import UpdateShareZoneForm1
from .forms import ResetPasswordForm
from .models import Notification_User
from .models import Notification
from .forms import LoginForm
from app.models import Tool
from app.models import Shed
from app.models import UserProfile
from app.models import ActiveTransactions
from app.models import ToolHistory
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.context_processors import csrf
from django.http import Http404
from .forms import UpdatePasswordForm
from .forms import TransactionCompletionForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.templatetags import DiggPaginator
from django.http import HttpResponse
from django.contrib import messages
import os
from django.conf import settings


def default_context(request):
    context_instance = {
                        'year': datetime.now().year,
                        'user_profile':UserProfile.objects.get(user_id=request.user.id)
                        }
    return context_instance


def home(request):
    """Renders the home page."""
    if request.user.is_authenticated() == False:
        return render(request, 'app/index.html')

    context_instance = default_context(request)
    assert isinstance(request, HttpRequest)
    form = SearchToolForm(request.GET)
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    zip_code = user_profile.zipcode
    objects_per_page = 25
    page = request.GET.get('page')
    tool_name = request.GET.get('tool_name')
    context_instance['search_form'] = SearchToolForm(request.GET)
    context_instance['shed_info'] = Shed.objects.get(zipcode=zip_code.zipcode)
    context_instance['user_profile'] = user_profile
    print(tool_name)
    if tool_name is None or not tool_name:
        print('tool_name is either empty or None')
        tool_name = ""
        tool = Tool.objects.all().filter(~Q(tool_owner_id=request.user.id), status="Active", is_borrowed=False, share_zone=zip_code)
    else:
        print('tool name is not empty and is not None')
        tool = Tool.objects.all().filter(~Q(tool_owner_id=request.user.id), status="Active", is_borrowed=False, share_zone=zip_code).filter(tool_name__contains=tool_name)
        if not tool:
            context_instance['message'] = 'Search resulted with no matching.'

    context_instance['tool_name'] = tool_name
    if tool.count() > objects_per_page:
        page_pagination(page,tool,objects_per_page,context_instance)
    else:
        context_instance['tool'] = tool
    notifications_shown = updateNotifications(request,context_instance)
    return render(request,
                  'app/index.html',
                  context_instance)


def page_pagination(page, query, objects_per_page,context_instance):
    if page is None:
        page = 1
    print(str(page) + "=page")
    try:
        print('before custom_paginator')
        custom_paginator = DiggPaginator(query, objects_per_page, body=3, padding=1, tail=1).page(page)
        print('after custom paginator')
        context_instance['paginator'] = custom_paginator
    except:
        print('in except')
        raise Http404("Page not found")
    paging = Paginator(query, objects_per_page)
    tool = paging.page(page)
    context_instance['tool'] = tool


def contact(request):
    """Renders the contact page."""
    if request.user.is_authenticated():
        context_instance = default_context(request)
        context_instance['title'] = 'Contact'
        context_instance['message'] = ''
        context_instance['year'] = datetime.now().year
        assert isinstance(request, HttpRequest)
        return render(request, 'app/contact.html',context_instance)
    else:
        return render(request,
                      'app/contact.html',
                      context_instance=RequestContext(request,
                                                      {
                                                          'title': 'Contact',
                                                          'message': '',
                                                          'year': datetime.now().year,
                                                      }))

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    if request.user.is_authenticated():
        context_instance = default_context(request)
        context_instance.update(csrf(request))
        context_instance['title'] = 'About Us'
        context_instance['message'] = ''
        context_instance['year'] = datetime.now().year
        return render(request, 'app/about.html',context_instance)
    else:
        return render(request,
                      'app/about.html',
                      context_instance=RequestContext(request,
                                                      {
                                                          'title': 'About Us',
                                                          'message': '',
                                                          'year': datetime.now().year,
                                                      }))

def login(request):
    title = 'Login page.'
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            entered_user = form.data['username']
            entered_password = form.data['password']
            user = auth.authenticate(username=entered_user, password=entered_password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/')
            else:
                form = LoginForm()
                error = True
                return render(request, 'app/login.html', {'form': form, 'title': title, 'error': error})
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form, 'title': title})


def register(request):
    if request.user.is_authenticated():
        raise Http404(
            "You are already logged in. So please go to the main site.")
    form = RegisterUserForm(initial={'gender': '1'})
    return render(request,
                  'app/registeruser.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      'title': 'Register',
                                                      'message': '',
                                                      'year': datetime.now().year,
                                                      'form': form,
                                                  }), )


def create_user_profile(shed, form, user):
    user_p = UserProfile.objects.create(address=form.data['address'],
                                        gender=form.data['gender'],
                                        zipcode=shed,
                                        user_id=user)
    user_p.save()
    return user_p


def registerUser(request):
    title = 'Registration'
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)  # binding the form.
        if form.is_valid():
            user = User.objects.create_user(first_name=form.data['first_name'],
                                            last_name=form.data['last_name'],
                                            email=form.data['e_mail'],
                                            username=form.data['username'],
                                            password=form.data['password'],
                                            )
            user.save()
            entered_zipcode = form.data['zipcode']
            try:
                shed = Shed.objects.get(zipcode=entered_zipcode)
                create_user_profile(shed, form, user)
                form = LoginForm()
                title = 'You have successfully been registered. Please login.'
                return render(request, 'app/login.html', {'form': form, 'title': title})
            except:  # there are no zipcode values to that one
                title = 'You have been assigned as the coordinator of the Shed.'
                shed = Shed.objects.create(zipcode=entered_zipcode)
                shed.save()
                user_profile = create_user_profile(shed, form, user)
                user_profile.is_coordinator = True
                user_profile.save()
                form = ShedCreation()
                return render(request, 'app/registershed.html', {'form': form, 'title': title, 'zipcode': entered_zipcode, 'actn':'new_registration'})
    else:
        form = RegisterUserForm()
        title = 'Register'
    return render(request, 'app/registeruser.html', {'form': form, 'title': title})


def register_shed(request, zipcode, actn):
    """
    :param request:holds the page that calls register_shed function
    :return: register shed page, where the user creates the shed for the first time.
    """
    print('in register_shed')
    print(actn)
    if request.method == 'POST':
        form = ShedCreation(request.POST)
        if form.is_valid():
            shed = Shed.objects.get(zipcode=zipcode)

            print('add........................', form.data['address'])
            print('name........................', form.data['name'])

            shed.address = form.data['address']
            shed.name = form.data['name']
            shed.save()
        else:
            return render(request, 'app/registershed.html', {'form': form, 'zipcode': zipcode, 'actn': actn})

        if actn == 'updatesharezone':
            messages.success(request, 'Zipcode updated successfully')
            return HttpResponseRedirect('/updateUserInfo2')
        elif actn == 'new_registration':
            loginform = LoginForm()
            title = 'You have been successfully registered. Now, you can login and see what your new share zone offers to you.'
            return render(request, 'app/login.html', {'form': loginform, 'title': title})
    else:
        form = ShedCreation()
        return render(request, 'app/registershed.html', {'form': form, 'zipcode': zipcode, 'actn': 'new_registration'})


def registerTool(request):
    if request.method == 'POST':
        form = RegisterToolForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = UserProfile.objects.get(user_id=request.user.id)
            zip_code = user_profile.zipcode
            tool = Tool(tool_name=form.data['tool_name'],
                        status=form.data['status'],
                        category=form.data['category'],
                        tool_owner_id=request.user,
                        location=form.data['location'],
                        condition=form.data['condition'],
                        special_instruction=form.data['special_instruction'],
                        image=request.FILES['image'],
                        share_zone=Shed.objects.get(zipcode=UserProfile.objects.get(user_id=request.user.id).zipcode.zipcode),
                        )
            tool.save()
            messages.success(request, 'New tool has been registered successfully')
            return HttpResponseRedirect('/registeredTools')

    else:
        form = RegisterToolForm()
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)

    act = "Register"
    title = "Register Tool"
    context_instance = default_context(request)
    notifications_shown = updateNotifications(request,context_instance)
    context_instance.update(csrf(request))
    context_instance['form'] = form
    context_instance['id'] = id
    context_instance['act'] = act
    context_instance['title'] = title
    context_instance['user_profile'] = user_profile

    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    context_instance['user_profile'] = user_profile
    return render(request, 'app/registertool.html', context_instance)


def displayShedTools(request):
    context_instance = default_context(request)
    assert isinstance(request, HttpRequest)
    current_user = request.user.id
    is_tool_set_for_return = []
    user_profile = UserProfile.objects.get(user_id=current_user)
    zip_code = user_profile.zipcode
    shed_coordinators = UserProfile.objects.filter(zipcode=zip_code)
    notifications = Notification_User.objects.filter(isSeen=False,notification=Notification.objects.get(code='CVR')).filter(user__in=[user.user_id for user in shed_coordinators])
    for n in notifications:
        n.isSeen=True
        print(n)
        n.save()
    shed_tools = Tool.objects.filter(share_zone=zip_code)
    for t in shed_tools:
        print()
        try:
            is_tool_set_for_return.append(ActiveTransactions.objects.get(tool=t.id))
        except:
            is_tool_set_for_return.append(None)

    return_val = zip(shed_tools, is_tool_set_for_return)
    context_instance['shed_tools']=return_val

    updateNotifications(request, context_instance)
    return render(request,
                  'app/shedtooltable.html',
                    context_instance
                  )

def displayShedUsers(request):
    context_instance= default_context(request)
    assert isinstance(request, HttpRequest)
    notifications = Notification_User.objects.filter(isSeen=False,notification=Notification.objects.get(code='NC'),user=request.user)
    for n in notifications:
        n.isSeen=True
        n.save()
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    zip_code = user_profile.zipcode
    shed_users_profile = UserProfile.objects.all().filter(zipcode=zip_code).exclude(user_id=current_user)
    context_instance['users'] = shed_users_profile
    updateNotifications(request,context_instance)
    return render(request,
                  'app/shedusers.html',
                    context_instance
                  )

def assignNewCoordinator(request,user_id):
    context_instance = default_context(request)
    new_coordinator= UserProfile.objects.get(user_id=user_id)
    new_coordinator.is_coordinator=True
    notification_type = Notification.objects.get(code='NC')
    notification_sent = Notification_User(notification=notification_type, tool_name=None, user=User.objects.get(id=new_coordinator.user_id.id))
    notification_sent.save()
    new_coordinator.save()
    messages.success(request, 'A new user has been successfuly assigned as share zone coordinator.')
    return HttpResponseRedirect('/shareZoneUsers')


def displayShedStatisticsCat(request):
    context_instance= default_context(request)
    updateNotifications(request,context_instance)
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    zip_code = user_profile.zipcode

    common_tool = Tool.objects.all().filter(share_zone=zip_code, category='Common Use')
    context_instance['ctotal'] = len(common_tool)
    context_instance['active_ctotal'] = len(common_tool.filter(status='Active'))
    context_instance['borrow_ctotal'] = len(common_tool.filter(is_borrowed=True))

    garden_tool = Tool.objects.all().filter(share_zone=zip_code, category='Gardening')
    context_instance['gtotal'] = len(garden_tool)
    context_instance['active_gtotal'] = len(garden_tool.filter(status='Active'))
    context_instance['borrow_gtotal'] = len(garden_tool.filter(is_borrowed=True))

    wood_tool = Tool.objects.all().filter(share_zone=zip_code, category='Wood Working')
    context_instance['wtotal'] = len(wood_tool)
    context_instance['active_wtotal'] = len(wood_tool.filter(status='Active'))
    context_instance['borrow_wtotal'] = len(wood_tool.filter(is_borrowed=True))

    metal_tool = Tool.objects.all().filter(share_zone=zip_code, category='Metal Working')
    context_instance['mtotal'] = len(metal_tool)
    context_instance['active_mtotal'] = len(metal_tool.filter(status='Active'))
    context_instance['borrow_mtotal'] = len(metal_tool.filter(is_borrowed=True))

    cleaning_tool = Tool.objects.all().filter(share_zone=zip_code, category='Cleaning')
    context_instance['cltotal'] = len(cleaning_tool)
    context_instance['active_cltotal'] = len(cleaning_tool.filter(status='Active'))
    context_instance['borrow_cltotal'] = len(cleaning_tool.filter(is_borrowed=True))

    kitchen_tool = Tool.objects.all().filter(share_zone=zip_code, category='Kitchen')
    context_instance['ktotal'] = len(kitchen_tool)
    context_instance['active_ktotal'] = len(kitchen_tool.filter(status='Active'))
    context_instance['borrow_ktotal'] = len(kitchen_tool.filter(is_borrowed=True))

    other_tool = Tool.objects.all().filter(share_zone=zip_code, category='Others')
    context_instance['ototal'] = len(other_tool)
    context_instance['active_ototal'] = len(other_tool.filter(status='Active'))
    context_instance['borrow_ototal'] = len(other_tool.filter(is_borrowed=True))

    assert isinstance(request, HttpRequest)
    return render(request,
                  'app/shedCommunityStatisticsCat.html',
                    context_instance
                  )

def displayShedStatistics(request):
    context_instance= default_context(request)
    updateNotifications(request,context_instance)
    assert isinstance(request, HttpRequest)
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    zip_code = user_profile.zipcode
    shed_users = UserProfile.objects.all().filter(zipcode=zip_code)
    shed_tool = Tool.objects.all().filter(share_zone=zip_code, location='Shed')
    home_tool = Tool.objects.all().filter(share_zone=zip_code, location='Home')

    borrowed_tool= ActiveTransactions.objects.all().filter(tool=shed_tool, is_set_for_return=False)
    return_tool= ActiveTransactions.objects.all().filter(tool=shed_tool, is_set_for_return=True)
    home_borrowed_tool= ActiveTransactions.objects.all().filter(tool=home_tool, is_set_for_return=False)
    home_return_tool= ActiveTransactions.objects.all().filter(tool=shed_tool, is_set_for_return=True)

    context_instance['borrowedct'] = len(borrowed_tool)
    context_instance['returnct'] = len(return_tool)
    context_instance['homeBorrowedct'] = len(home_borrowed_tool)
    context_instance['homeReturnct'] = len(home_return_tool)
    context_instance['shedct'] = len(shed_tool)
    context_instance['homect'] = len(home_tool)

    highest_tool_ct = 0
    tool_owner=[]
    for index in range(len(shed_users)):
        current_tool_ct = len(Tool.objects.all().filter(share_zone=zip_code))
        print (current_tool_ct)
        tool_active_ct = len(Tool.objects.all().filter(share_zone=zip_code, status='Active'))
        if current_tool_ct >= highest_tool_ct:
            highest_tool_ct = current_tool_ct
            if shed_users[index].user_id_id not in tool_owner:
                tool_owner.append(shed_users[index].user_id)
    context_instance['hiToolCt'] = highest_tool_ct
    context_instance['hiOwner'] = tool_owner
    context_instance['activect'] = tool_active_ct

    last_week = len(ToolHistory.objects.all().filter(Q(tool_id=shed_tool)| Q(tool_id=home_tool), transaction_type='Returned', return_date__gte=datetime.now()-timedelta(days=7)))
    context_instance['weekBorrowed'] = last_week

    this_month = len(ToolHistory.objects.all().filter(Q(tool_id=shed_tool)| Q(tool_id=home_tool), transaction_type='Returned', return_date__gte=datetime.now()-timedelta(days=30)))
    context_instance['monthBorrowed'] = this_month

    last_month = len(ToolHistory.objects.all().filter(Q(tool_id=shed_tool)| Q(tool_id=home_tool), transaction_type='Returned', return_date__lte=datetime.now()-timedelta(days=30)))
    context_instance['lastMonthBorrowed'] = last_month

    return render(request,
                  'app/shedCommunityStatistics.html',
                    context_instance
                  )

def displayToolHistory(request,id):
    tool = Tool.objects.get(id=id)
    context_instance= default_context(request)
    updateNotifications(request, context_instance)
    assert isinstance(request, HttpRequest)
    current_user = request.user.id
    context_instance['tool'] = tool
    context_instance['toolname'] = tool.tool_name
    history=ToolHistory.objects.all().filter(tool_id=id)
    if len(history)>0:
        print(history)
        context_instance['history'] = history
        return render(request,
                  'app/displayToolHistory.html',
                    context_instance
                  )
    else:
        messages.warning(request, 'You have no completed transaction history for this tool')
        return HttpResponseRedirect('/registeredTools')


def registeredTools(request):
    tools = Tool.objects.all().filter(tool_owner_id=request.user.id)
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    context_instance  = default_context(request)
    context_instance['tools'] = tools
    updateNotifications(request,context_instance)
    return render(request,
                  'app/registeredtools.html',
                  context_instance)


def lentTools(request):
    context_instance = default_context(request)
    user_notifications = Notification_User.objects.all().filter(user=request.user.id).filter(isSeen=False).filter(notification=Notification.objects.get(code='TR'))
    for i in user_notifications:
        print(i.tool_name)
        print(i.user)
    print('before the call')
    context_instance['user_notifications'] = user_notifications
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    is_tool_set_for_return = []
    tools = Tool.objects.all().filter(tool_owner_id=request.user.id, is_borrowed=True)
    if tools:
        context_instance['lentTools'] = True
    for t in tools:
        print()
        try:
            is_tool_set_for_return.append(ActiveTransactions.objects.get(tool=t.id))
        except:
            is_tool_set_for_return.append(None)
    return_val = zip(tools, is_tool_set_for_return)
    for t in tools:
        try:
            print(t)
            print('before tool_notify')
            tool_notify = Notification_User.objects.all().filter(tool_name=t.id).filter(notification=Notification.objects.get(code='TR'))
            print('after tool_notify')
            print(tool_notify)
            for t in tool_notify:
                t.isSeen=True
                t.save()
                print(t.isSeen)
            tool_notify.save()
            print(tool_notify.isSeen)
        except:
            print('Tool does not have a notification')
    updateNotifications(request,context_instance)
    context_instance['zipped_data'] = return_val

    return render(request,
                  'app/lentTools.html',
                  context_instance,
                    )


def borrowedTools(request):
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    context_instance = default_context(request)
    user_notifications = Notification_User.objects.all().filter(user=request.user.id).filter(isSeen=False).filter(notification=Notification.objects.get(code='AR'))
    for i in user_notifications:
        print(i.tool_name)
        print(i.user)
    print('before the call')
    context_instance['user_notifications'] = user_notifications
    borrow_request_notifications = Notification_User.objects.filter(user=request.user, isSeen=False).filter(notification__in=[Notification.objects.get(code='AR'), Notification.objects.get(code='RR'), Notification.objects.get(code='VR')])
    for c in borrow_request_notifications:
        print(c)
        c.isSeen = True
        c.save()
    updateNotifications(request,context_instance)
    context_instance['borrowedTools']= ActiveTransactions.objects.filter(borrower_id=request.user.id, is_request_approved=True, is_set_for_return=False)
    return render(request,'app/borrowedtools.html', context_instance)


def borrowRequests(request):
    current_user = request.user.id
    context_instance=default_context(request)
    user_profile = UserProfile.objects.get(user_id=current_user)

    user_notifications = Notification_User.objects.all().filter(user=request.user.id).filter(isSeen=False).filter(notification=Notification.objects.get(code='BR'))
    context_instance['user_notifications'] = user_notifications
    for i in user_notifications:
        print(i.tool_name.tool_name)
        print(i.user_id)

    requested_tools = ActiveTransactions.objects.filter(owner_id=request.user.id, is_request_approved=False, is_set_for_return=False)
    borrow_request_notifications = Notification_User.objects.filter(user=request.user, notification=Notification.objects.get(code='BR'), isSeen=False)

    for c in borrow_request_notifications:
        c.isSeen = True
        c.save()
    updateNotifications(request,context_instance)
    context_instance['requestedTools'] = ActiveTransactions.objects.filter(owner_id=request.user.id, is_request_approved=False, is_set_for_return=False)
    return render(request, 'app/borrowrequest.html',context_instance)


def updateUserInfo(request):
    if request.POST:
        value = request.user.id
        current_user = User.objects.get(id=value)
        form = UpdatePersonalInfoForm(request.POST)
        if form.is_valid():
            form = UpdatePersonalInfoForm(request.POST, instance=value)
            form.save()
            return HttpResponseRedirect('/')
    else:
        value = request.user.id
        current_user = User.objects.get(id=value)
        user_profile = UserProfile.objects.get(user_id=value)
        form = UpdatePersonalInfoForm(instance=current_user)

    user_profile = UserProfile.objects.get(user_id=current_user)

    context_instance = default_context(request)
    notifications_shown = updateNotifications(request,context_instance)
    context_instance.update(csrf(request))
    context_instance['form'] = form
    context_instance['last_name'] = current_user.last_name
    context_instance['first_name'] = current_user.first_name
    context_instance['email'] = current_user.email
    context_instance['address'] = user_profile.address
    context_instance['gender'] = user_profile.gender
    context_instance['zipcode'] = user_profile.zipcode.zipcode
    context_instance['form_name'] = False
    context_instance['form_email'] = False
    context_instance['form_address'] = False
    context_instance['form_gender'] = False
    context_instance['form_update'] = False
    context_instance['update_name'] = 'updatename'
    context_instance['update_email'] = 'updateemail'
    context_instance['update_address'] = 'updateaddress'
    context_instance['update_gender'] = 'updategender'
    context_instance['user_profile'] = user_profile
    return render(request, 'app/updateuserinfo2.html', context_instance)


def onReturnToolRequest(request, toolid):
    requested_tool = ActiveTransactions.objects.get(tool=toolid)
    requested_tool.is_set_for_return = True
    tool = Tool.objects.get(id=toolid)
    tool_return_date = getattr(requested_tool, "return_date")
    if tool_return_date != datetime.now():
        requested_tool.return_date = datetime.now()
        # requested_tool.notification_info = 'requestToolReturn'
    requested_tool.save()
    if requested_tool.tool.location == 'Home':
        notification_type = Notification.objects.get(code="TR")
        Notification_User(tool_name=requested_tool.tool, user=requested_tool.owner_id, notification=notification_type).save()
    else:
        print('tool is from the shed')
        shed_coordinators = UserProfile.objects.filter(is_coordinator=True)
        for i in shed_coordinators:
            print(i.user_id)
        current_user = UserProfile.objects.get(user_id=request.user)
        print(current_user.user_id)
        try:
            #the user who is returning the tool is a shed coordinator?
            UserProfile.objects.filter(is_coordinator=True).get(user_id=current_user.user_id)
            print('shed coordinator is borrower of the tool')
            toolHistory = ToolHistory(tool_id=tool,
                                      borrower_id=request.user,
                                      owner_id=tool.tool_owner_id,
                                      transaction_date=datetime.now(),
                                      condition='Like New',
                                      transaction_type='Returned',
                                      owner_comments='',
                                      return_date=datetime.now(),
                                      )
            tool.is_borrowed = False
            tool.condition = 'Like New'
            toolHistory.save()
            tool.save()
            requested_tool.delete()
            messages.success(request, 'Tool has been successfully returned.')
            return HttpResponseRedirect('/displayShedTools')
        except:
            print ('in except of the get for shed_coordinators')
            notification_type = Notification.objects.get(code="CVR")
            for coordinator in shed_coordinators:
                Notification_User(tool_name=requested_tool.tool, user=coordinator.user_id, notification=notification_type).save()
    messages.success(request, 'A return request has been sent successfully')
    return HttpResponseRedirect('/borrowedTools')


def onApproveReturn(request, toolid):
    context_instance = default_context(request)
    requested_tool = ActiveTransactions.objects.get(tool=toolid)
    tool = Tool.objects.get(id=toolid)
    tool_owner = User.objects.get(id=tool.tool_owner_id.id)
    borrower = getattr(requested_tool, "borrower_id")
    return_date = getattr(requested_tool, "return_date")
    notification_type = Notification.objects.get(code="VR")
    print(request.method)
    form = TransactionCompletionForm()
    if request.method == 'POST':
        form = TransactionCompletionForm(request.POST)
        print('inside post')
        if form.is_valid():
            print('form is valid')
            print(borrower)
            print(request.user)
            print(form.data['condition'])
            toolHistory = ToolHistory(tool_id=tool,
                                      borrower_id=borrower,
                                      owner_id=tool_owner,
                                      transaction_date=datetime.now(),
                                      condition=form.data['condition'],
                                      transaction_type='Returned',
                                      owner_comments=form.data['message'],
                                      return_date=return_date,
                                      )
            tool.is_borrowed = False
            tool.condition = form.data['condition']
            toolHistory.save()
            tool.save()
            Notification_User(notification=notification_type, tool_name=tool, user=borrower).save()
            requested_tool.delete()
            messages.success(request, 'Tool return has been approved')
            if tool.location =='Shed':
                return HttpResponseRedirect('/displayShedTools')
            else:
                return HttpResponseRedirect('/lentTools')
    updateNotifications(request,context_instance)
    context_instance['tool']= tool
    context_instance['form']= form
    context_instance['tool_owner']= tool_owner
    return render(request, 'app/toolreturn.html',context_instance)


def onRejectToolRequest(request, toolid):
    notification_type = Notification.objects.get(code="RR")
    tool = Tool.objects.get(id=toolid)
    tool.is_borrowed = False
    tool.save()
    requested_tool = ActiveTransactions.objects.get(tool=toolid)
    Notification_User(tool_name=tool, user=requested_tool.borrower_id, notification=notification_type).save()
    requested_tool.delete()
    messages.success(request, 'Tool request has been rejected')
    return HttpResponseRedirect('/borrowRequests')


# AL: This method stores the borrower and the tool owner as foreign key to the borrow request table
# This makes the notification functionality easy.
def onBorrowToolRequest(request, id):
    print('in on borrow tool request')
    tool = Tool.objects.get(id=id)
    context_instance = default_context(request)
    updateNotifications(request,context_instance)
    notification_type = Notification.objects.get(code='BR')
    tool_owner = User.objects.get(id=tool.tool_owner_id.id)
    borrower_id = User.objects.get(id=request.user.id)
    form = TransactionCompletionForm()
    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            activeTransaction = ActiveTransactions(tool=tool,
                                                   borrower_id=borrower_id,
                                                   owner_id=tool_owner,
                                                   is_request_approved=False,
                                                   return_date=form.data['date'],
                                                   borrower_message=form.data['message'],
                                                   )
            activeTransaction.save()
            tool.is_borrowed = True
            tool.save()
            if tool.location == 'Shed':
                activeTransaction.is_request_approved = True
                activeTransaction.save()
                onAcceptToolRequest(request, id)
                messages.success(request, 'The tool has been borrowed successfully')
            else:
                notification_sent = Notification_User(notification=notification_type, tool_name=tool, user=tool_owner)
                notification_sent.save()
                messages.success(request, 'A borrow request has been sent successfully')
            return HttpResponseRedirect('/')
    context_instance['tool']= tool
    context_instance['form'] = form
    context_instance['tool_owner'] = tool_owner
    return render(request, 'app/tooldetails.html', context_instance)


def onAcceptToolRequest(request, toolid):
    print('In accept request')
    requested_tool = ActiveTransactions.objects.get(tool=toolid)
    requested_tool.is_request_approved = True
    requested_tool.save()
    notification_type = Notification.objects.get(code='AR')
    borrower = getattr(requested_tool, "borrower_id")
    borrower_id = getattr(borrower, "id")
    return_date = getattr(requested_tool, "return_date")

    # update tool with tool_id borrower ID
    tool = Tool.objects.get(id=toolid)

    tool.save()

    toolHistory = ToolHistory(tool_id=tool,
                              borrower_id=borrower,
                              owner_id=request.user,
                              transaction_date=datetime.now(),
                              condition=tool.condition,
                              transaction_type='Borrowed',
                              owner_comments='Request has been accepted.',
                              return_date=return_date,
                              borrower_message=requested_tool.borrower_message,
                              )
    toolHistory.save()
    # update the notifications in ActiveTransactions model
    accepted_tool = ActiveTransactions.objects.get(tool=toolid)
    Notification_User(notification=notification_type,user=borrower,tool_name=tool).save()
    # accepted_tool.notification_info = 'acceptToolRequest'
    accepted_tool.save()

    if tool.location != 'Shed':
        messages.success(request, 'The tool request has been accepted')
    return HttpResponseRedirect('/borrowRequests')


def updateTool(request, id):
    tools = Tool.objects.get(id=id)
    title = "Update Tool Information"
    if request.POST:
        form = UpdateToolsForm(request.POST, instance=tools)
        if form.is_valid():
            tools.save()
            form.save()
            messages.success(request, 'Tool information has been updated successfully')
            return HttpResponseRedirect('/registeredTools')
    else:
        form = UpdateToolsForm(instance=tools)

    act = "Update"
    context_instance = default_context(request)
    updateNotifications(request, context_instance)
    context_instance.update(csrf(request))
    context_instance['form'] = form
    context_instance['image'] = request.FILES.get('image')
    context_instance['tools'] = tools
    context_instance['id'] = id
    context_instance['act'] = act
    context_instance['title'] = title
    return render(request, 'app/updateTool.html', context_instance)



def changePwd(request):
    message = ''

    context_instance = default_context(request)
    updateNotifications(request, context_instance)
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            uid = request.user.id
            u = User.objects.get(id=uid)
            #password_1 = request.POST['password_1'].encode('ascii', 'replace')
            #password_2 = request.POST['password_2'].encode('ascii', 'replace')
            #if password_1 == password_2:
            u.set_password(form.data['password_1'])
            u.save()
            return HttpResponseRedirect('/')
        else:
            context_instance['form'] = form
            context_instance.update(csrf(request))
            return render_to_response('app/changepwd.html', context_instance)
    else:
        form = UpdatePasswordForm()
        context_instance['form']= form
        context_instance.update(csrf(request))
        return render(request, 'app/changepwd.html', context_instance)


def updatedetails(request, actn):
    form_update = False
    form_name = False
    form_email = False
    form_address = False
    form_gender = False
    redirect = False
    form = ''
    print('action',actn)
    current_user = User.objects.get(id=request.user.id)
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    if request.POST:
        form_update = True
        msg = ''
        if actn == "updatename":
            form = UpdatePersonalInfoForm(request.POST)
            form_name = True
            if form.is_valid():
                form = UpdatePersonalInfoForm(request.POST, instance=current_user)
                form.save()
                msg = 'Name updated successfully'
                redirect = True

        if actn == "updateemail":
            form = UpdatePersonalInfoForm2(request.POST)
            form_email = True
            if form.is_valid():
                form = UpdatePersonalInfoForm2(request.POST, instance=current_user)
                form.save()
                redirect = True
                msg = 'Email updated successfully'

        if actn == "updateaddress":
            form = UpdateUserProfileForm(request.POST)
            form_address = True
            if form.is_valid():
                form = UpdateUserProfileForm(request.POST, instance=user_profile)
                form.save()
                msg = 'Address updated successfully'
                redirect = True
                form_address = True
        if actn == "updategender":
            form = UpdateUserProfileForm2(request.POST)
            if form.is_valid():
                form = UpdateUserProfileForm2(request.POST, instance=user_profile)
                form.save()
                msg = 'Gender updated successfully'
                redirect = True
        if redirect:
            messages.success(request, msg)
            return HttpResponseRedirect('/updateUserInfo2')
    else:

        if actn == "updatename":
            form = UpdatePersonalInfoForm(instance=current_user)
            form_name = True
            form_update = True
        if actn == "updateemail":
            form = UpdatePersonalInfoForm2(instance=current_user)
            form_email = True
            form_update = True
        if actn == "updateaddress":
            form = UpdateUserProfileForm(instance=user_profile)
            form_address = True
            form_update = True
        if actn == "updategender":
            form = UpdateUserProfileForm2(instance=user_profile)
            form_gender = True
            form_update = True


    context_instance = default_context(request)
    notifications_shown = updateNotifications(request,context_instance)
    context_instance.update(csrf(request))
    context_instance['form'] = form
    context_instance['last_name'] = current_user.last_name
    context_instance['first_name'] = current_user.first_name
    context_instance['email'] = current_user.email
    context_instance['zipcode'] = user_profile.zipcode.zipcode
    context_instance['address'] = user_profile.address
    context_instance['gender'] = user_profile.gender
    context_instance['form_update'] = form_update
    context_instance['form_name'] = form_name
    context_instance['form_email'] = form_email
    context_instance['form_address'] = form_address
    context_instance['form_gender'] = form_gender
    context_instance['user_profile'] = user_profile

    return render(request, 'app/updateuserinfo2.html', context_instance)


def updateNotifications(request,context):
    user_notifications = Notification_User.objects.all().filter(user=request.user.id).filter(isSeen=False)
    notifications = user_notifications.count()
    if notifications is None:
        notifications=0
    for i in user_notifications:
        print(i.tool_name)
        print(i.user)
    context['notifications_shown'] = notifications
    context['br'] = user_notifications.filter(notification=Notification.objects.get(code='BR')).count()
    context['rr'] = user_notifications.filter(notification=Notification.objects.get(code='RR')).count()
    context['ar'] = user_notifications.filter(notification=Notification.objects.get(code='AR')).count()
    context['vr'] = user_notifications.filter(notification=Notification.objects.get(code='VR')).count()
    context['tr'] = user_notifications.filter(notification=Notification.objects.get(code='TR')).count()
    if UserProfile.objects.get(user_id=request.user.id).is_coordinator:
            context['cvr'] = user_notifications.filter(notification=Notification.objects.get(code='CVR')).count()
            context['nc'] = user_notifications.filter(notification=Notification.objects.get(code='NC'))



def resetPassword(request):
    context_instance = default_context(request)
    if request.method == 'POST':

        form = ResetPasswordForm(request.POST, request.FILES)
        if form.is_valid():
            form = LoginForm()
            messages.success(request, 'Password sent successfully')
            context_instance['form'] = form
            return render(request, 'app/login.html', context_instance)
    else:
        form = ResetPasswordForm()
        context_instance['form'] = form
    return render(request, 'app/resetPassword.html', context_instance)


def changeShareZone(request):
    print('sharezone change - 1')
    hasBorrowed = False
    hasLent = False
    current_user = User.objects.get(id=request.user.id)
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    currentZip = user_profile.zipcode.zipcode

    is_admin = user_profile.is_coordinator

    if request.method == 'POST':
        print('sharezone change - 11')
        form = UpdateShareZoneForm2(request.POST)
        print('sharezone change - 11')
        if form.is_valid():
            entered_zipcode = form.data['zipcode']
            print(entered_zipcode)
            try:
                print('sharezone change - 2')
                shed = Shed.objects.get(zipcode=entered_zipcode)
                user_profile.zipcode = shed
                user_profile.is_coordinator = True
                user_profile.save()
                update_tools(request, entered_zipcode)
                messages.success(request, 'Zipcode updated successfully')
                return HttpResponseRedirect('/updateUserInfo2')
            except:  # there are no zipcode values to that one
                # print('sharezone change - 3')
                title = 'You have been assigned as the coordinator of the Shed.'
                shed = Shed.objects.create(zipcode=entered_zipcode)
                shed.save()
                user_profile.zipcode = shed
                user_profile.is_coordinator = True
                user_profile.save()
                form = ShedCreation()
                msg = 'Zipcode updated successfully'
                update_tools(request, entered_zipcode)
                delete_sharezone(request, currentZip)
                return render(request, 'app/registershed.html', {'form': form, 'title': title, 'zipcode': entered_zipcode, 'actn':'updatesharezone'})

        return render(request, 'app/changeShareZone.html')
    else:
        lentTools = ActiveTransactions.objects.filter(owner_id=request.user.id,
                                                      is_request_approved=True,
                                                      is_set_for_return=False)
        borrwedTools = ActiveTransactions.objects.filter(borrower_id=request.user.id,
                                                      is_request_approved=True,
                                                      is_set_for_return=False)
        has_admin = has_admins(request)

        if borrwedTools:
            print('user has borrowed tools')
            hasBorrowed = True
        if lentTools:
            print('user has lent tools')
            hasLent = True
        if not has_admin:
            print(' admin to be appointed')

        context_instance = default_context(request)
        context_instance.update(csrf(request))
        context_instance['form'] = UpdateShareZoneForm2()
        context_instance['hasBorrowed'] = hasBorrowed
        context_instance['hasLent'] = hasLent
        context_instance['zipcode'] = currentZip
        context_instance['has_admin'] = has_admin
        context_instance['is_admin'] = is_admin
        return render(request, 'app/changeShareZone.html', context_instance)


def has_admins(request):
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    current_user_is_admin = user_profile.is_coordinator
    zip_code = user_profile.zipcode
    sharezone_users = UserProfile.objects.all().filter(zipcode=zip_code).exclude(user_id=current_user)
    has_admin = True
    if sharezone_users:
        has_admin = False
        shed_coordinators = UserProfile.objects.all().filter(zipcode=zip_code, is_coordinator=True).exclude(user_id=current_user)
        if shed_coordinators:
            has_admin = True
    return has_admin


def update_tools(request, zip):

    shed = Shed.objects.get(zipcode=zip)
    tools = Tool.objects.all().filter(tool_owner_id=request.user.id)

    for i in tools:
        i.share_zone = shed
        i.save()


def delete_sharezone(request, old_zip):
    print('delete zip')
    current_user = request.user.id

    other_users = UserProfile.objects.all().filter(zipcode=zip).exclude(user_id=current_user)
    print('Other users are registered for the shed')
    count = other_users.count()
    if count==0:
        print('deleting........zip')
        shed = Shed.objects.get(zipcode=old_zip)
        print('Shed',shed.zipcode)
        shed.delete()
