from django.shortcuts import render,  redirect
from django.http import HttpResponse, JsonResponse  
from .models import *
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

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
            question_objs = question_objs.filter(types__name__icontains = request.GET.get('types'))
            
        question_objs = list(question_objs)
        data = []
        random.shuffle(question_objs)
        
        
        for question_obj in question_objs:
            
            data.append({
                "uid" : question_obj.uid,
                "types": question_obj.types.name,
                "question": question_obj.question,
                "marks": question_obj.marks,
                "answer" : question_obj.get_answers(),
            })

        payload = {'status': True, 'data': data}
        
        return JsonResponse(payload)
        
    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong")

@csrf_exempt
def submit_quiz(request):
    try:
        if request.method == "POST":
            score = 0
            data = json.loads(request.body)
            answers = data.get('answers', [])
            quiz_type_name = data.get('quiz_type', None)
            quiz_type_obj = None
            if quiz_type_name:
                try:
                    quiz_type_obj = Types.objects.get(name=quiz_type_name)
                except Types.DoesNotExist:
                    quiz_type_obj = None

            print("Received answers:", answers)  # Debug print
            for item in answers:
                try:
                    question = Question.objects.get(uid=item.get('uid'))
                    selected_answer = item.get('selected')
                    print(f"Question: {question.question}, Selected: {selected_answer}")  # Debug print
                    if selected_answer and question.question_answer.filter(answer=selected_answer, is_correct=True).exists():
                        score += question.marks or 1
                except Question.DoesNotExist:
                    continue  # or handle as needed

            if request.user.is_authenticated:
                UserScore.objects.create(
                    user=request.user,
                    score=score,
                    taken_at=timezone.now(),
                    quiz_type=quiz_type_obj
                )
            return JsonResponse({'score': score})
        return JsonResponse({'error': 'Invalid request'}, status=400)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='login')
def profile(request):
    user_scores = UserScore.objects.filter(user=request.user).order_by('-taken_at').select_related('quiz_type')
    return render(request, 'profile.html', {'user_scores': user_scores})

@login_required(login_url='login')
def leaderboard(request):
    from django.db.models import Max
    # Aggregate highest score per user
    top_scores = UserScore.objects.values('user__username').annotate(max_score=Max('score')).order_by('-max_score')[:10]
    return render(request, 'leaderboard.html', {'top_scores': top_scores})

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

