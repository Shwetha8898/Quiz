from django.shortcuts import render,  redirect
from django.http import HttpResponse, JsonResponse  
from .models import *
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Result

@login_required(login_url='login')
def home(request):
    context = {'categories': Types.objects.all()}
    
    if request.GET.get('types'):
        return redirect(f"/quiz/?types={request.GET.get('types')}")
    
    return render(request, 'home.html', context)

def quiz(request):
    context = {'types': request.GET.get('types')}
    return render(request, 'quiz.html', context)


def get_quiz(request):
    try:
        question_objs = Question.objects.all()
        
        if request.GET.get('types'):
            # FIXED filter
            question_objs = question_objs.filter(types__name__icontains=request.GET.get('types'))
            
        question_objs = list(question_objs)
        data = []
        random.shuffle(question_objs)
        
        for question_obj in question_objs:
            data.append({
                "uid": question_obj.uid,
                "types": question_obj.types.name,
                "question": question_obj.question,
                "marks": question_obj.marks,
                "answer": question_obj.get_answers(),
            })

        payload = {'status': True, 'data': data}
        return JsonResponse(payload)
        
    except Exception as e:
        print(e)
        # Return JSON error for frontend
        return JsonResponse({'status': False, 'error': str(e)}, status=500)

def submit_quiz(request):
    if request.method == "POST":
        score = 0
        data = request.POST.getlist('questions[]')
        
        for item in data:
            question = Question.objects.get(uid=item.get('uid'))
            selected_answer = item.get('selected')
            
            if question.answer_set.filter(answer=selected_answer, is_correct=True).exists():
                score += question.marks or 1
        
            # Save the result to the database
                if request.user.is_authenticated:
                  result = Result.objects.create(
                    user=request.user,
                    score=score,
                    types=question.types.name,
                    total=len(data)
                    )
                result.save()
        
        return redirect(f"/score/?score={score}")
    
    return HttpResponse("Invalid request")

def score(request):
    score = request.GET.get('score', 0)
    return render(request, 'score.html', {'score': score})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('home')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Create your views here.
