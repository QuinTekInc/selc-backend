from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Department)
admin.site.register(models.Student)
admin.site.register(models.Lecturer)
admin.site.register(models.Course)
admin.site.register(models.ClassCourse)
admin.site.register(models.StudentClass)
admin.site.register(models.QuestionCategory)
admin.site.register(models.Questionnaire)
admin.site.register(models.Evaluation)
admin.site.register(models.EvaluationSuggestion)
admin.site.register(models.LecturerRating)
admin.site.register(models.EvaluationStatus)
admin.site.register(models.GeneralSetting)
admin.site.register(models.Notification)
