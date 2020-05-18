from django.shortcuts import render,redirect
from django.http import HttpResponse
from rating_app.models import credited_courses_table, rating_table
from django.contrib.auth import logout
from . import forms

def home(request):
    logout(request)
    request.session.set_test_cookie()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return render(request,'home.html')
    else:
        return HttpResponse('Your browser does not accept cookies.')

def success(request):
        if not request.user.is_authenticated:
            return HttpResponse('Login to Google first')
        mail=str(request.user.email)
        if not (mail[-11:] == '@nitc.ac.in'):
            return HttpResponse('You are not authenticated to evaluate any courses. Ensure that you are using NITC mail id.')
        roll=mail[-20:-11]
        obj=credited_courses_table.objects.filter(roll_no=roll)
        if not len(obj):
            return HttpResponse("You don't seem to have registered for any courses. Contact your faculty advisor.")
        request.session['roll']=roll
        request.session.set_expiry(1200)
        return redirect('/rate/')

def rate(request):
    if not request.user.is_authenticated:
            return HttpResponse('Login to Google first')
    if not request.session.get('roll'):
        return HttpResponse('Please go to login page. The session might have expired')
    request.session.set_expiry(1200)
    roll=str(request.session['roll'])

    if request.method=='GET':
        obj=credited_courses_table.objects.filter(roll_no=roll,feedback_status=0)
        if not obj.exists():
            return HttpResponse('You have completed the evaluation. Thank you.')
        listt=[]
        for o in obj:
            listt.append(o.course_name + ' - ' + o.faculty_name)
        return render(request,'rate.html',{'listt':listt})
    else:
        pair = request.POST['pair']
        pos = pair.find('-')
        cname = pair[:pos-1]
        fname = pair[pos+2:]
        obj=credited_courses_table.objects.filter(roll_no = roll, course_name = cname, faculty_name = fname)
        obj = obj[0]
        if obj.feedback_status == 1:
            return HttpResponse('You have already rated this course.')
        obj.feedback_status = 1
        obj.save()
        obj = rating_table.objects.filter(course_name = cname, faculty_name = fname)
        obj = obj[0]
        rep = request.POST
        obj.question_1 = obj.question_1 + int(rep['star1'])
        obj.question_2 = obj.question_2 + int(rep['star2'])
        obj.question_3 = obj.question_3 + int(rep['star3'])
        obj.question_4 = obj.question_4 + int(rep['star4'])
        obj.question_5 = obj.question_5 + int(rep['star5'])
        obj.question_6 = obj.question_6 + int(rep['star6'])
        obj.question_7 = obj.question_7 + int(rep['star7'])
        obj.count = obj.count + 1
        obj.save()

        obj=credited_courses_table.objects.filter(roll_no=roll,feedback_status=0)
        if not obj.exists():
            return HttpResponse('You have completed the evaluation. Thank you.')
        listt=[]
        for o in obj:
            listt.append(o.course_name + ' - ' + o.faculty_name)
        return render(request,'rate.html',{'listt':listt})

# Create your views here.
