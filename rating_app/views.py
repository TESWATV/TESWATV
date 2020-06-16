import csv,io
from django.http import HttpResponse
from django.shortcuts import render,redirect
from rating_app.models import credited_courses_table,rating_table
from . import forms
from django.contrib.auth import logout

class details:
    def __init__(self,cname,fname,display,status,id):
        self.cname = cname
        self.fname = fname
        self.display = display
        self.status = status
        self.id = id

def home(request):
    logout(request)
    request.session.set_test_cookie()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return render(request,'home.html')
    else:
        return render(request,'error.html',{'text':'Your browser does not accept cookies. Cookies are necessary for this website to function properly.'} )

def success(request):
        if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'Google login failure. Logout and try again.'} )
        mail=str(request.user.email)
        if mail == 'coursefeedback@nitc.ac.in':
            request.session['roll']=mail
            request.session.set_expiry(14400)
            return redirect('/admin/')
        if mail == 'pathari@gmail.com':
            roll = 'pathari'
        elif mail == 'pathari@nitc.ac.in':
            roll = 'pathari2'
        else:
            if not (mail[-11:] == '@nitc.ac.in'):
                return render(request,'error.html',{'text':'You are not authenticated to evaluate any courses. Go to home page and try again. Ensure that you are using NITC mail id.' } )
            roll=mail[-20:-11]
        obj=credited_courses_table.objects.filter(roll_no=roll)
        if not len(obj):
            return render(request,'error.html',{'text':"You don't seem to have registered for any courses. Contact your faculty advisor." } )
        request.session['roll']=roll
        request.session.set_expiry(1200)
        return redirect('/rate/')

def rate(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    request.session.set_expiry(1200)
    roll=str(request.session['roll'])
    if request.method=='GET':
        obj=credited_courses_table.objects.filter(roll_no=roll)
        completed = 1
        id = 1
        listt = []
        for o in obj:
            cname = o.course_name
            fname = o.faculty_name
            display = cname + ' | PROF. ' + fname
            status = o.feedback_status
            listt.append(details(cname,fname,display,status,str(id)))
            id = id + 1
            if status == 0:
                completed =0

        return render(request,'rate.html',{'listt':listt, 'completed':completed } )
    else:
        cname = request.POST['cname']
        fname = request.POST['fname']
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

        obj=credited_courses_table.objects.filter(roll_no=roll)
        completed = 1
        id = 1
        listt = []
        for o in obj:
            cname = o.course_name
            fname = o.faculty_name
            display = cname + ' | PROF. ' + fname
            status = o.feedback_status
            listt.append(details(cname,fname,display,status,str(id)))
            id = id + 1
            if status == 0:
                completed =0
        return render(request,'rate.html',{'listt':listt, 'completed':completed } )


def admin(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="admin.html"
        return render(request,template)
    else :
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def evaluation_progress(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        if request.method=="GET":
            template="evaluation_progress.html"
            form=forms.progress()
            var1=credited_courses_table.objects.values('roll_no','feedback_status').order_by('roll_no','feedback_status').distinct('roll_no','feedback_status')
            list_result = [entry for entry in var1]
            for list in list_result:
                list['roll_no']=list['roll_no'].upper()

            l=len(list_result)
            i=0
            while i < l-1:
                if list_result[i]["roll_no"]==list_result[i+1]["roll_no"]:
                    list_result[i+1].update({"feedback_status": False})
                i=i+1

            b = []
            for i in range(0, len(list_result)):
                if list_result[i] not in list_result[i+1:]:
                    b.append(list_result[i])

            return render(request,template,{'form':form,'abcd':b})
        else:
            form=forms.progress(request.POST)
            template="evaluation_progress.html"
            if form.is_valid():
                status=form.cleaned_data['Status']
                department=form.cleaned_data['Roll_no_ends_with']
                department=department.lower()
                status2=status
                status=int(status)
                if status == 1 :
                    statusname = 'Completed'
                elif status == 0 :
                    statusname = 'Pending'

                if credited_courses_table.objects.filter(feedback_status=status,roll_no__endswith=department).exists() :
                    q1=credited_courses_table.objects.filter(roll_no__endswith=department).values('roll_no','feedback_status').order_by('roll_no','feedback_status').distinct('roll_no','feedback_status')

                    list_result1 = [entry for entry in q1]
                    for list in list_result1:
                        list['roll_no']=list['roll_no'].upper()

                    l=len(list_result1)
                    i=0
                    while i < l-1:
                        if list_result1[i]["roll_no"]==list_result1[i+1]["roll_no"]:
                            list_result1[i+1].update({"feedback_status": False})
                        i=i+1

                    b = []
                    for i in range(0, len(list_result1)):
                        if list_result1[i] not in list_result1[i+1:] and list_result1[i]["feedback_status"] == status:
                            b.append(list_result1[i])

                    return render(request,template,{'abcd':b,'status':statusname,'department':department,'form':form})
                else :
                    return render(request,template,{'form':form,'message':'No matching rows','title':'Evaluation Progress'})
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })



def detailed_statistics(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        if request.method=="GET":
            template="detailed_statistics.html"
            form=forms.details()
            var1=rating_table.objects.values().order_by('faculty_name')
            sum=[]
            i=0
            for var in var1:
                if var['count'] == 0 :
                    sum.append(0.00)
                else :
                    t = var['question_1']+var['question_2']+var['question_3']+var['question_4']+var['question_5']+var['question_6']+var['question_7']
                    t = (t/(7*5*var['count']))*100
                    t = float("{:.2f}".format(round(t, 2)))
                    sum.append(t)
                i=i+1

            list_result = [entry for entry in var1]
            i=0
            for s in sum:
                list_result[i].update({"average": sum[i]})
                i=i+1

            return render(request,template,{'form':form,'abcd2':list_result ,'sum':sum})
        else:
            form=forms.details(request.POST)
            if form.is_valid():
                a=form.cleaned_data['faculty_name']
                if a.startswith('Prof. ') :
                    a=a[6:]
                b=form.cleaned_data['course_name']

                if rating_table.objects.filter(faculty_name__icontains=a,course_name__icontains=b).exists() :

                    var1=rating_table.objects.values().filter(faculty_name__icontains=a,course_name__icontains=b).order_by('faculty_name')
                    sum=[]
                    i=0
                    for var in var1:
                        if var['count'] == 0 :
                            sum.append(0.00)
                        else :
                            t = var['question_1']+var['question_2']+var['question_3']+var['question_4']+var['question_5']+var['question_6']+var['question_7']
                            t = (t/(7*5*var['count']))*100
                            t = float("{:.2f}".format(round(t, 2)))
                            sum.append(t)
                        i=i+1

                    list_result = [entry for entry in var1]
                    i=0
                    for s in sum:
                        list_result[i].update({"average": sum[i]})
                        i=i+1

                    return render(request,'detailed_statistics.html',{'form':form,'abcd2':list_result ,'sum':sum})

                else :
                    return render(request,'detailed_statistics.html',{'message':'Row does not exist','title':'Evaluation Progress','form':form})
            else :
                return render(request,'message.html',{'message':'Form is not valid','title':'Evaluation Progress'})
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def detailed_statistics_2(request) :
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        #var1 = request.POST['avg']
        var1 = request.POST.get('avg',None)
        fname = request.POST.get('fname',None)
        cname = request.POST.get('cname',None)
        var2 = rating_table.objects.get(faculty_name=fname,course_name=cname)
        if var2.count == 0 :
            a=1
        else :
            var2.question_1=(var2.question_1 /(5*var2.count))*100
            var2.question_1 = float("{:.2f}".format(round(var2.question_1, 2)))
            var2.question_2=(var2.question_2 /(5*var2.count))*100
            var2.question_2 = float("{:.2f}".format(round(var2.question_2, 2)))
            var2.question_3=(var2.question_3 /(5*var2.count))*100
            var2.question_3 = float("{:.2f}".format(round(var2.question_3, 2)))
            var2.question_4=(var2.question_4 /(5*var2.count))*100
            var2.question_4 = float("{:.2f}".format(round(var2.question_4, 2)))
            var2.question_5=(var2.question_5 /(5*var2.count))*100
            var2.question_5 = float("{:.2f}".format(round(var2.question_5, 2)))
            var2.question_6=(var2.question_6 /(5*var2.count))*100
            var2.question_6 = float("{:.2f}".format(round(var2.question_6, 2)))
            var2.question_7=(var2.question_7 /(5*var2.count))*100
            var2.question_7 = float("{:.2f}".format(round(var2.question_7, 2)))

        num8=0 #NITC Average Score

        q1=q2=q3=q4=q5=q6=q7=count=0 #Average score for each question
        for a in rating_table.objects.exclude(count=0):
            q1=q1+a.question_1
            q2=q2+a.question_2
            q3=q3+a.question_3
            q4=q4+a.question_4
            q5=q5+a.question_5
            q6=q6+a.question_6
            q7=q7+a.question_7
            count=count+a.count

        count=count*5
        q1 = (q1 /(count))*100
        q2 = (q2 /(count))*100
        q3 = (q3 /(count))*100
        q4 = (q4 /(count))*100
        q5 = (q5 /(count))*100
        q6 = (q6 /(count))*100
        q7 = (q7 /(count))*100
        num8 = num8+q1+q2+q3+q4+q5+q6+q7
        num8 = num8 / 7
        q1 = float("{:.2f}".format(round(q1, 2)))
        q2 = float("{:.2f}".format(round(q2, 2)))
        q3 = float("{:.2f}".format(round(q3, 2)))
        q4 = float("{:.2f}".format(round(q4, 2)))
        q5 = float("{:.2f}".format(round(q5, 2)))
        q6 = float("{:.2f}".format(round(q6, 2)))
        q7 = float("{:.2f}".format(round(q7, 2)))
        num8 = float("{:.2f}".format(round(num8, 2)))

        template="detailed_statistics_2.html"
        data=credited_courses_table.objects.filter(faculty_name=fname,course_name=cname,feedback_status=False)
        count2=len(data)
        return render(request,template,{'avg':var1,'abcd':var2, 'fname':fname,'cname':cname,'count2':count2,'num8':num8,'q1':q1,'q2':q2,'q3':q3,'q4':q4,'q5':q5,'q6':q6,'q7':q7})
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def overall_statistics(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        num1=0 #Total no. of evaluations
        for a in rating_table.objects.all():
            num1=num1+a.count
        num2=0 #Total no. of students participated
        for b in credited_courses_table.objects.values('roll_no').distinct().exclude(feedback_status=False):
            num2=num2+1
        num3=0 #Total no. of teachers rated at least once
        for c in rating_table.objects.values('faculty_name').distinct().exclude(count=0):
            num3=num3+1
        num4=0 #Total no. of courses rated at least once
        for d in rating_table.objects.values('course_name').distinct().exclude(count=0):
            num4=num4+1
        num5=0 #Pending evaluations
        for e in credited_courses_table.objects.filter(feedback_status=False):
            num5=num5+1
        num6=0 #Pending courses
        for e in credited_courses_table.objects.distinct('course_name','faculty_name').filter(feedback_status=False):
            num6=num6+1
        num7=0 #Pending students
        for e in credited_courses_table.objects.distinct('roll_no').filter(feedback_status=False):
            num7=num7+1

        num8=0 #NITC Average Score

        q1=q2=q3=q4=q5=q6=q7=count=0 #Average score for each question
        for a in rating_table.objects.exclude(count=0):
            q1=q1+a.question_1
            q2=q2+a.question_2
            q3=q3+a.question_3
            q4=q4+a.question_4
            q5=q5+a.question_5
            q6=q6+a.question_6
            q7=q7+a.question_7
            count=count+a.count

        count=count*5
        q1 = (q1 /(count))*100
        q2 = (q2 /(count))*100
        q3 = (q3 /(count))*100
        q4 = (q4 /(count))*100
        q5 = (q5 /(count))*100
        q6 = (q6 /(count))*100
        q7 = (q7 /(count))*100
        num8 = num8+q1+q2+q3+q4+q5+q6+q7
        num8 = num8 / 7
        q1 = float("{:.2f}".format(round(q1, 2)))
        q2 = float("{:.2f}".format(round(q2, 2)))
        q3 = float("{:.2f}".format(round(q3, 2)))
        q4 = float("{:.2f}".format(round(q4, 2)))
        q5 = float("{:.2f}".format(round(q5, 2)))
        q6 = float("{:.2f}".format(round(q6, 2)))
        q7 = float("{:.2f}".format(round(q7, 2)))
        num8 = float("{:.2f}".format(round(num8, 2)))


        return render(request,'overall_statistics.html',{'num1':num1,'num2':num2,'num3':num3,'num4':num4,'num5':num5,'num6':num6,'num7':num7,'num8':num8,'q1':q1,'q2':q2,'q3':q3,'q4':q4,'q5':q5,'q6':q6,'q7':q7,'count':count})
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def database(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="database.html"
        return render(request,template)
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def save_database(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="save_database.html"
        return render(request,template)
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def save_database_1(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        response1 = HttpResponse(content_type='text/csv')
        response1['Content-Disposition'] = 'attachment; filename="credited_courses_table.csv"'
        writer = csv.writer(response1)
        writer.writerow(['roll_no', 'faculty_name', 'course_name', 'feedback_status'])
        rows = credited_courses_table.objects.all()
        for row in rows:
            writer.writerow([row.roll_no.upper(),row.faculty_name,row.course_name,row.feedback_status])
        return response1
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def save_database_2(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        response2 = HttpResponse(content_type='text/csv')
        response2['Content-Disposition'] = 'attachment; filename="rating_table.csv"'
        writer = csv.writer(response2)
        writer.writerow(['faculty_name', 'course_name', 'question_1', 'question_2', 'question_3', 'question_4', 'question_5', 'question_6', 'question_7', 'count'])
        rows = rating_table.objects.all()
        for row in rows:
            writer.writerow([row.faculty_name,row.course_name,row.question_1,row.question_2,row.question_3,row.question_4,row.question_5,row.question_6,row.question_7,row.count])
        return response2
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def delete_database(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="delete_database.html"
        return render(request,template)
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def check(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="check_delete_database.html"
        return render(request,template)
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def delete(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="message.html"
        credited_courses_table.objects.all().delete()
        rating_table.objects.all().delete()
        return render(request,template,{'message':'Successfully deleted','title':'Delete Database'})
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def update_database(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="update_database_options.html"
        return render(request,template)
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def update_database_dss(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="update_database_dss.html"
        prompt={
            'order' : 'Order of CSV file should be , roll no., teacher no., faculty name, course name'
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
                roll_no=column[1].lower(),
                faculty_name=column[3],
                course_name=column[4],
                feedback_status = False
            )
            _, created = rating_table.objects.update_or_create(
                faculty_name=column[3],
                course_name=column[4],
                question_1 = 0,
                question_2 = 0,
                question_3 = 0,
                question_4 = 0,
                question_5 = 0,
                question_6 = 0,
                question_7 = 0,
                count = 0
            )
        template="message.html"
        return render(request,template,{'message':'Successfully uploaded','title':'Update Database'})
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })

def update_database_saved(request):
    if not request.user.is_authenticated:
            return render(request,'error.html',{'text':'You need to log in with Google first. Go to home page and try again.'} )
    if not request.session.get('roll'):
        return render(request,'error.html',{'text':'Please go to home page and log in with Google again. The session might have expired' })
    roll=str(request.session['roll'])
    if roll=='coursefeedback@nitc.ac.in':
        request.session.set_expiry(14400)
        template="update_database_saved.html"
        prompt={
            'order1' : 'Order of CSV file should be roll no., faculty name, course name, feedback_status',
            'order2' : 'Order of CSV file should be faculty name, course name, question 1, question 2, question 3, question 4, question 5, question 6, question 7, count'
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
                roll_no=column[0].lower(),
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
        template="message.html"
        return render(request,template,{'message':'Successfully uploaded','title':'Update Database'})
    else:
        return render(request,'error.html',{'text':'You are not authenticated to access this page.' })
