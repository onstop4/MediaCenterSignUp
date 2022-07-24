from django.contrib import admin

from signup.models import ClassPeriod, ClassPeriodSignUp, StudentInfo, User

admin.site.register(User)
admin.site.register(StudentInfo)
admin.site.register(ClassPeriod)
admin.site.register(ClassPeriodSignUp)
