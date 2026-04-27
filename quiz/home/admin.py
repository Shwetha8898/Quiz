from django.contrib import admin
from .models import *

# Register your models here.

class AnswerAdmin(admin.StackedInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerAdmin]

class ResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'types', 'total', 'created_at']
    search_fields = ['user__username', 'types__name']
    list_filter = ['created_at']

admin.site.register(Types)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Result, ResultAdmin)
#admin.site.register(ResultAdmin)