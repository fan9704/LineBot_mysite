from django.views.generic.detail import DetailView,SingleObjectMixin
from django.views.generic.base import View,TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers
from django import http
from django.urls import resolvers
from django.contrib.auth.forms import UserCreationForm
from mysites.form import CommentForm,LoginForm
import django
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import redirect, render
from django import template
from django.template.loader import get_template
from django.template import RequestContext, context
from mysites.models import Restaurant,Food,Comment
from django.views.generic.edit import FormView
# Create your views here.
from django.http import HttpResponse, request,HttpResponseRedirect, response,Http404

def index(request):
    return render(request,'Teamwork.html',locals())

def meta(request):
    values=request.META.items()
    values.sort()
    html=[]
    for k,v in values:
        html.append('<tr><td>{0}</td><td>{1}</td></tr>'.format(k,v))
    return HttpResponse('<table>{0}</table>'.format('\n'.join(html)))

def welcome(request):
    if 'user_name' in request.GET and request.GET['user_name'] != '':
        return HttpResponse('Welcome!~'+request.GET['user_name'])
    else:
        return render(request,'welcome.html',locals())

@login_required
def list(request, model):
    objs = model.objects.all()
    return render(request, '{0}s_list.html'.format(model.__name__.lower()), locals())
# class MenuView(DetailView):
#     model = Restaurant
#     template_name = 'menu.html'
#     context_object_name = 'restaurant'

#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(MenuView, self).dispatch(request, *args, **kwargs)

#     def get(self, request, pk, *args, **kwargs):
#         try:
#             return super(MenuView, self).get(self, request, pk=pk, *args, **kwargs)
#         except Http404:
#             return HttpResponseRedirect('/restaurants_list/')
def menu(request,id=1):
    path=request.path
    if 'id' in request.GET and request.GET['id'] != '':
        restaurants=Restaurant.objects.get(id=request.GET['id'])
        return render(request,'menu.html',locals())
    else:
        return HttpResponseRedirect("/restaurants_list/")
def user_can_comment(user):
    return user.is_authenticated and user.has_perm('restaurants.can_comment')

@user_passes_test(user_can_comment, login_url='/accounts/login/')
def comment(request,id):
    if request.user.is_authenticated and request.user.has_perm('restaurants.can_comment'):
        if id:
            r=Restaurant.objects.get(id=id)
    else:
        return HttpResponseRedirect("/restaurants_list/")
    errors=[]
    
    if request.POST:
        f= CommentForm(request.POST)
        if f.is_valid():
            visitor=f.cleaned_data['visitor']
            content=f.cleaned_data['content']
            email=f.cleaned_data['email']
            date_time=timezone.localtime(timezone.now())
            c=Comment.objects.create(visitor=visitor,email=email,content=content,date_time=date_time,restaurant=r)
            f=CommentForm(initial={'content':'我沒意見'})
    else:
         f=CommentForm(initial={'content':'我沒意見'})
      
    return render(request,'comments.html',locals())

def set_c(request):
    reseponse=HttpResponse('Set your lucky_number as 8')
    response.set_cookie('lucky_number',8)
    return response

def get_c(request):
    if 'lucky_number' in request.COOKIES:
        return HttpResponse('Your luck_number is {0} '.format(request.COOKIES['lucky_number']))
    else:
        return HttpResponse('No cookies.')

def use_session(request):
    request.session['lucky_number']=8
    if 'lucky_number' in request.session:
        lucky_number=request.session['lucky_number']
        response=HttpResponse('Your lucky_number is '+lucky_number)
    del request.session['lucky_number']
    return response

def session_test(request):
    sid=request.COOKIES['sessionid']
    sid2=request.session.session_key
    s=Session.objects.get(pk=sid)
    s_info='Session ID:' +sid+'<br>SessionID2:'+sid2+'<br>Expire_date:'+str(s.expire_date)+'<br>Date:'+str(s.get_decoded())
    return HttpResponse(s_info)

def sign_in(request):
    form = LoginForm()
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/index/')  #重新導向到首頁
    context = {
        'form': form
    }
    return render(request, 'login.html', context)
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect('/accounts/login/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', locals())

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/index/')

class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        # 取得字典型態的Context
        context = super().get_context_data(**kwargs)
        # 加入我們額外想要的時間參數
        context["time"] = timezone.now()
        return context
