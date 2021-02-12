from django.db import models

class credited_courses_table(models.Model):
    roll_no = models.CharField(max_length = 15)
    faculty_name = models.CharField(max_length = 150)
    course_name = models.CharField(max_length = 150)
    feedback_status = models.BooleanField()

    class Meta:
        #managed = False
        db_table = 'credited_courses_table'

class rating_table(models.Model):
    faculty_name = models.CharField(max_length = 150)
    course_name = models.CharField(max_length = 150)
    question_1 = models.IntegerField()
    question_2 = models.IntegerField()
    question_3 = models.IntegerField()
    question_4 = models.IntegerField()
    question_5 = models.IntegerField()
    question_6 = models.IntegerField()
    question_7 = models.IntegerField()
    count = models.IntegerField()

    class Meta:
        db_table = 'rating_table'
