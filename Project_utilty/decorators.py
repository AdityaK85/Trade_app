import traceback
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from algosee_app.models import *
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from functools import wraps



### check request is authenticated or not 
def is_authenticated(request):
    try:
        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')
		
        if user_type and user_id:
            if user_type == 'user':
                user_obj = UserAccount.objects.get(id=user_id)
            else:
                user = Admin_Login.objects.get(id=user_id)
            return user
        else:
            return None
    except:
        traceback.print_exc()
    return None

def is_admin_authenticated(request):
    try:
		
        user_type = request.session.get('admin_user_type')
        user_id = request.session.get('admin_user_id')
		
        if user_type and user_id:
            if user_type == 'admin':
                user = Admin_Login.objects.get(id=user_id)
            else:
                user = MyUser.objects.get(id=user_id)
            return user
        else:
            return None
    except:
        traceback.print_exc()
    return None



def handle_admin_page_exception(func):
	'''Function template to handle POST request and handle exceptions...'''
	def wrapper(request, *args, **kwargs):
		try:
			user = is_admin_authenticated(request)
			if user:
				return func(request, user, *args, **kwargs)
			else:
				return redirect('/')
		except:
			traceback.print_exc()
		return render(request, 'error_page.html')
		# return HttpResponse('Something went wrong')
	return wrapper

def is_client_authenticated(request):
    try:
		
        user_id = request.session.get('client_userId')
        user_type = request.session.get('user_type')
		
        if user_type and user_id:
            if user_type == 'Client':
                user = MyUser.objects.get(id=user_id)
            return user
        else:
            return None
    except:
        traceback.print_exc()
    return None


def handle_client_page_exception(func):
	'''Function template to handle POST request and handle exceptions...'''
	def wrapper(request, *args, **kwargs):
		try:
			user = is_client_authenticated(request)
			
			if user:
				return func(request, user, *args, **kwargs)
			else:
				return redirect('/')
		except:
			traceback.print_exc()
		# return render(request, 'error_page.html')
		return redirect('/')
		# return HttpResponse('Something went wrong')
	return wrapper

def handle_page_exception(func):
	'''Function template to handle POST request and handle exceptions...'''
	def wrapper(request, *args, **kwargs):
		try:
			user = is_authenticated(request)
			
			if user:
				print(user, '>>>>>>>.')
				# if user.status == 'Blocked':
				# 	return redirect('/Logout/')
				return func(request, user, *args, **kwargs)
			else:
				return redirect('/')
		except:
			traceback.print_exc()
		return HttpResponse('Something went wrong')
	return wrapper

def handle_ajax_exception(func):
	'''Function template to handle POST request and handle exceptions...'''
	def wrapper(request, *args, **kwargs):
		send_data = {'status': 0, 'msg': 'Something went wrong.'}
		try:
			if request.method == 'POST':
				return func(request, *args, **kwargs)
			else:
				send_data['msg'] = 'POST method required.'
		except ObjectDoesNotExist:
			send_data['msg'] = 'Object not found.'
		except:
			traceback.print_exc()
		return JsonResponse(send_data)
	return wrapper


def get_date_label(posted_date, todays_date):
    yesterday = todays_date - timedelta(days=1)
    if todays_date == posted_date.date():
        return "Today"
    elif yesterday == posted_date.date():
        return "Yesterday"
    else:
        return posted_date.date().strftime("%d-%m-%Y")