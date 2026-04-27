from django.contrib import admin
from .models import *
from .models import UserScore

# Register your models here.

class AnswerAdmin(admin.StackedInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerAdmin]

admin.site.register(Types)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)


@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'taken_at')
    list_filter = ('user',)