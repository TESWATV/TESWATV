import csv,io
from django.http import HttpResponse
from django.shortcuts import render,redirect
from rating_app.models import credited_courses_table,rating_table
from . import forms
from django.contrib.auth import logout

def home(request):
    logout(request)
    request.session.set_test_cookie()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return render(request,'home2.html')
    else:
        return render(request,'error.html',{'text':'Your browser does not accept cookies. Cookies are necessary for this website to function properly.'} )

def success(request):
        if not request.user.is_authenticated:
            logout(request)
            return render(request,'error.html',{'text':'Google login failure. Logout and try again.'} )
        mail=str(request.user.email)
        if not (mail[-11:] == '@nitc.ac.in'):
            logout(request)
            return render(request,'error.html',{'text':'You are not authenticated to evaluate any courses. Go to home page and try again. Ensure that you are using NITC mail id.' } )
        roll=mail[-20:-11]
        obj=credited_courses_table.objects.filter(roll_no=roll)
        if not len(obj):
            logout(request)
            return render(request,'error.html',{'text':"You don't seem to have registered for any courses. Contact your faculty advisor." } )
        logout(request)
        request.session['roll']=roll
        request.session.set_expiry(1200)
        return redirect('/rate/')

def rate(request):
    #if not request.user.is_authenticated:
    #        return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    request.session.set_expiry(1200)
    roll=str(request.session['roll'])
    #feedback_status is passed down
    if request.method=='GET':
        obj=credited_courses_table.objects.filter(roll_no=roll)
        listt={}
        completed = 1
        for o in obj:
            key=str(o.course_name + ' | ' + o.faculty_name)
            listt[key] = int(o.feedback_status)
            if o.feedback_status == 0:
                completed =0

        return render(request,'rate3.html',{'listt':listt, 'completed':completed } )
    else:
        pair = request.POST['pair']
        pos = pair.find('|')
        cname = pair[:pos-1]
        fname = pair[pos+2:]
        obj=credited_courses_table.objects.filter(roll_no = roll, course_name = cname, faculty_name = fname)
        obj = obj[0]
        if obj.feedback_status == 1:
            return render(request,'double_rate.html')
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

        return redirect('/rate/')

def admin(request):
    template="admin.html"
    return render(request,template)

def evaluation_progress(request):
    if request.method=="GET":
        template="evaluation_progress.html"
        form=forms.progress()
        return render(request,template,{'form':form})
    else:
        form=forms.progress(request.POST)
        template="evaluation_progress.html"
        if form.is_valid():
            status=form.cleaned_data['Status']
            department=form.cleaned_data['Roll_no_ends_with']
            status=int(status)
            if status == 1 :
                statusname = 'Completed'
            elif status == 0 :
                statusname = 'Pending'

            if credited_courses_table.objects.filter(feedback_status=status).exists() :
                q1 = credited_courses_table.objects.filter(roll_no__endswith=department).distinct()
                q2 = q1.filter(feedback_status=status).values('roll_no')
                abcd=q2.values_list('roll_no', flat=True).order_by('roll_no')
                return render(request,template,{'abcd':abcd,'status':statusname,'department':department,'form':form})
            else :
                return HttpResponse('No matching rows')

def detailed_statistics(request):
    if request.method=="GET":
        template="detailed_statistics.html"
        form=forms.details()
        return render(request,template,{'form':form})
    else:
        form=forms.details(request.POST)
        if form.is_valid():
            a=form.cleaned_data['faculty_name']
            b=form.cleaned_data['course_name']
            if rating_table.objects.filter(faculty_name=a,course_name=b).exists() :
                abcd = rating_table.objects.get(faculty_name=a,course_name=b)
                ans=abcd.question_1+abcd.question_2+abcd.question_3+abcd.question_4+abcd.question_5+abcd.question_6+abcd.question_7
                ans=ans/7
                ans=ans/abcd.count
                perc=ans/5
                perc=perc*100
                text = str(perc) + "%"
                return render(request,'detailed_statistics.html',{'text':text,'abcd':abcd,'form':form,'fname':a,'cname':b})
            else :
                return HttpResponse('Does not exist')

def detailed_statistics_2(request):
    template="detailed_statistics_2.html"
    return render(request,template)

def overall_statistics(request):
    num1=0
    for a in rating_table.objects.all():
        num1=num1+a.count
    num2=0
    for b in credited_courses_table.objects.values('roll_no').distinct():
        num2=num2+1
    num3=0
    for c in rating_table.objects.values('faculty_name').distinct().exclude(count=0):
        num3=num3+1
    num4=0
    for d in rating_table.objects.values('course_name').distinct().exclude(count=0):
        num4=num4+1
    num5=0
    for e in credited_courses_table.objects.filter(feedback_status=False):
        num5=num5+1
    return render(request,'overall_statistics.html',{'num1':num1,'num2':num2,'num3':num3,'num4':num4,'num5':num5})

def database(request):
    template="database.html"
    return render(request,template)

def save_database(request):
    template="save_database.html"
    return render(request,template)

def save_database_1(request):
    response1 = HttpResponse(content_type='text/csv')
    response1['Content-Disposition'] = 'attachment; filename="credited_courses_table.csv"'
    writer = csv.writer(response1)
    writer.writerow(['roll_no', 'faculty_name', 'course_name', 'feedback_status'])
    rows = credited_courses_table.objects.all()
    for row in rows:
        writer.writerow([row.roll_no,row.faculty_name,row.course_name,row.feedback_status])
    return response1

def save_database_2(request):
    response2 = HttpResponse(content_type='text/csv')
    response2['Content-Disposition'] = 'attachment; filename="rating_table.csv"'
    writer = csv.writer(response2)
    writer.writerow(['faculty_name', 'course_name', 'question_1', 'question_2', 'question_3', 'question_4', 'question_5', 'question_6', 'question_7', 'count'])
    rows = rating_table.objects.all()
    for row in rows:
        writer.writerow([row.faculty_name,row.course_name,row.question_1,row.question_2,row.question_3,row.question_4,row.question_5,row.question_6,row.question_7,row.count])
    return response2

def delete_database(request):
    template="delete_database.html"
    #credited_courses_table.objects.all().delete()
    #rating_table.objects.all().delete()
    return render(request,template)

def update_database(request):
    template="update_database_options.html"
    return render(request,template)

def update_database_dss(request):
    template="update_database_dss.html"
    prompt={
        'order' : 'Order of CSV file should be roll no., faculty name, course name.'
    }
    if request.method == "GET":
        return render(request,template,prompt)
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'This is not a csv file')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = credited_courses_table.objects.update_or_create(
            roll_no=column[0],
            faculty_name=column[1],
            course_name=column[2],
            feedback_status = False
        )
        _, created = rating_table.objects.update_or_create(
            faculty_name=column[1],
            course_name=column[2],
            question_1 = 0,
            question_2 = 0,
            question_3 = 0,
            question_4 = 0,
            question_5 = 0,
            question_6 = 0,
            question_7 = 0,
            count = 0
        )
    context = {
    'order' : 'Successfully uploaded'
    }
    return HttpResponse('Successfully uploaded')

def update_database_saved(request):
    template="update_database_saved.html"
    prompt={
        'order1' : 'Order of CSV file should be roll no., faculty name, course name, feedback_status',
        'order2' : 'Order of CSV file should be faculty name,course name,question 1,question 2,question 3,question 4,question 5,question 6,question 7,count'
    }
    if request.method == "GET":
        return render(request,template,prompt)
    csv_file_1 = request.FILES['file1']
    if not csv_file_1.name.endswith('.csv'):
        messages.error(request, 'This is not a csv file')
    data_set = csv_file_1.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = credited_courses_table.objects.update_or_create(
            roll_no=column[0],
            faculty_name=column[1],
            course_name=column[2],
            feedback_status = column[3]
        )
    csv_file_2 = request.FILES['file2']
    if not csv_file_2.name.endswith('.csv'):
        messages.error(request, 'This is not a csv file')
    data_set = csv_file_2.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = rating_table.objects.update_or_create(
            faculty_name=column[0],
            course_name=column[1],
            question_1 = column[2],
            question_2 = column[3],
            question_3 = column[4],
            question_4 = column[5],
            question_5 = column[6],
            question_6 = column[7],
            question_7 = column[8],
            count = column[9]
        )
    context = {
    'order' : 'Successfully uploaded'
    }
    return HttpResponse('Successfully uploaded')
