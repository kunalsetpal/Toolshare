"""
Definition of urls for DjangoWebProject1.
"""

from datetime import datetime
from django.conf.urls import patterns, url
from app.forms import BootstrapAuthenticationForm
from django.conf import settings
from app import views
from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.static import static

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name='home'),
    url(r'^contact$', 'app.views.contact', name='contact'),
    url(r'^about', 'app.views.about', name='about'),
    url(r'^login/$', 'app.views.login', name='login'),
    url(r'^logout$',
        'django.contrib.auth.views.logout',
        {
            'next_page': '/',
        },
        name='logout'),

    # url(r'^reset/password_reset/$','django.contrib.auth.views.password_reset', name='reset_password_reset1'),
    # url(r'^reset/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    # url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
    url(r'^resetPassword/$', views.resetPassword, name='resetPassword'),
    url(r'^register/$', views.register, name='register'),
    url(r'^registerUser/$', views.registerUser, name='registerUser'),
    url(r'^registerUser/(?P<zipcode>[0-9]{1,5})/(?P<actn>.*)/$', views.register_shed, name='registershed'),
    url(r'^registerTool/$', views.registerTool, name='registerTool'),

    url(r'^lentTools/$', views.lentTools, name='lentTools'),


    url(r'^registeredTools/$', views.registeredTools, name='registeredTools'),

    url(r'^borrowedTools/$', views.borrowedTools, name='borrowedTools'),

    url(r'^borrowRequests/$', views.borrowRequests, name='borrowRequests'),
    url(r'^displayShedTools/$', views.displayShedTools, name='displayShedTools'),
    url(r'^shareZoneUsers/$', views.displayShedUsers, name='displayShedUsers'),
    url(r'^assignCoordinator/(?P<user_id>[0-9]+)/$', views.assignNewCoordinator, name='assignNewCoordinator'),
    url(r'^displayShedStatistics/$', views.displayShedStatistics, name='displayShedStatistics'),
    url(r'^displayShedStatisticsCat/$', views.displayShedStatisticsCat, name='displayShedStatisticsCat'),


    url(r'^registerShed/$', views.register_shed, name='registershed'),
    url(r'^registerTool/(?P<id>[0-9]+)/$', views.updateTool, name='updateTool'),
    url(r'^displayToolHistory/(?P<id>[0-9]+)/$', views.displayToolHistory, name='displayToolHistory'),
    url(r'^borrowToolRequest/(?P<id>[0-9]+)/$', views.onBorrowToolRequest, name='onBorrowToolRequest'),
    url(r'^acceptToolRequest/(?P<toolid>[0-9]+)/$', views.onAcceptToolRequest, name='onAcceptToolRequest'),
    url(r'^returnToolRequest/(?P<toolid>[0-9]+)/$', views.onReturnToolRequest, name='onReturnToolRequest'),
    url(r'^rejectToolRequest/(?P<toolid>[0-9]+)/$', views.onRejectToolRequest, name='onRejectToolRequest'),
    url(r'^approveReturn/(?P<toolid>[0-9]+)/$', views.onApproveReturn, name='onApproveReturn'),
    url(r'^$', 'app.views.home', name='onBorrowToolRequest'),
    url(r'^updateUserInfo/$', views.updateUserInfo, name='updateUserInfo'),
    url(r'^changePwd/$', views.changePwd, name='updatePwd'),
    url(r'^updateUserInfo2/$', views.updateUserInfo, name='updateUserInfo'),
    url(r'^updatedetails/(?P<actn>.*)/$', views.updatedetails, name='updatedetails'),
    url(r'^changeShareZone/$', views.changeShareZone, name='changeShareZone'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



