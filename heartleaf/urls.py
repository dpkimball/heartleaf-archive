from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from . import views

from heartleaf.registration import views as registration_views
from heartleaf.receipts import views as receipt_views

app_name = 'heartleaf'

urlpatterns = [
    url(r'^receipts/$', login_required(receipt_views.index), name='index'),

    url(r'^receipts/(?P<receipt_id>[0-9]+)/(?P<receipt_item_id>[0-9]+)/item$',
        login_required(receipt_views.receipt_item), name='receipt_item'),

    url(r'^receipts/(?P<receipt_id>[0-9]+)/$',
        login_required(receipt_views.receipt_detail), name='receipt_detail'),

    # url(r'^receipts/(?P<receipt_id>[0-9]+)/add/$', login_required(receipt_views.add), name='add'),

    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/signup/$', registration_views.UserSignUp.as_view(), name="signup"),

    url(r'^rest/users/register', views.register),
]
