"""gbs_zxiat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.views import serve as static_serve
from gbs_zxiat import settings
from django.contrib.auth.decorators import login_required
#from .api import urls as api_urls
from . import views, api
from . models import *
import time

admin.autodiscover()


urlpatterns = [
    #re_path(r'^static/(?P<path>.*)$', static_serve,
            #{'document_root': settings.STATICFILES_DIRS[0]}
           # ),  # django static
    path('admin/', admin.site.urls),
    path("data_handle/", views.data_handle), # 数据导入
    path("gb_gateway_devs/", views.gb_gateway_devs),
    # path("api/", include(api_urls.urlpatterns)),  # api 模块
    #path("", views.index), # 首页
    # path("test", views.test), # test
]


_apis_confs = []
for module in [i for i in dir(api)]:
    if module not in ("i", "os", "_") and not module.startswith("__"):
        # print("______", module)
        module_object = getattr(api, module)
        _vars = vars(module_object)
        for j in _vars:
            _ = _vars[j]
            if hasattr(_,"__call__"):
                # print(module_object,_)
                if hasattr(_, 'fun') or (  "request" in getattr(getattr(_,"__code__",None),"co_varnames",())):
                    # print(_.__name__,_,"111", j)
                    #print(_,_.fun)

                    if hasattr(_,"regex_rule"):
                        # 是一个api
                        if not  _.regex_rule:
                            urlpatterns.append((path("api/%s/%s" % (module,j),
                                                     _)))
                            _apis_confs.append([module,getattr(module_object,"__doc__") or '', "/api/%s/%s" % (module,j), _])
                        else:
                            urlpatterns.append((re_path(_.regex_rule,
                                                     _)))


                    else:
                        urlpatterns.append((path("api/%s/%s" % (module, j),
                                                 _)))




# api文档
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from collections import OrderedDict
from itertools import groupby
import config

def api_document(request):
    # api 文档
    _apis_confs.sort(key=lambda x: x[0])
    result = OrderedDict()
    for module_name, _iter in groupby(_apis_confs, key=lambda x: (x[0],x[1])):
        # print(module_name)
        result[module_name] = []
        for j in _iter:
            result[module_name].append((j[1],j[2], j[3].__doc__ or '', j[3].login_required))
    result = result.items()
    return render(request, "api_document.html", locals())


urlpatterns.append(path(r"api_document.html",api_document))
# urlpatterns.append(re_path(r"(.+?\.html)",
#                            login_required(lambda request, temp_name: render(request, temp_name,
#                                                                             dict(locals().items(),**{"config": config})))
#                            ))
urlpatterns.append(re_path(r"^(?P<path>.*)$", views.front_view))