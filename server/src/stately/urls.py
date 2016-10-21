"""stately URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/actor/$', views.get_or_forget_current_actor),
    url(r'^api/cases/awaiting/$', views.get_cases_awaiting_action),
    url(r'^api/cases/acted/$', views.get_cases_acted_on),
    url(r'^api/send-auth-token/$', views.send_auth_token),
    url(r'^api/authenticate/$', views.authenticate),

    # These must go at the end, since they will catch any URLs that fall
    # through.
    url(r'^api/(?P<workflow_slug>[a-z-]+)/$', views.get_workflow_or_create_case),
    url(r'^api/(?P<workflow_slug>[a-z-]+)/(?P<case_id>[a-zA-Z0-9-]+)/$', views.get_case),
    url(r'^api/(?P<workflow_slug>[a-z-]+)/(?P<case_id>[a-zA-Z0-9-]+)/(?P<action_slug>[a-z-]+)/$', views.create_event),
]
