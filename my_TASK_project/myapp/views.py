# myapp/views.py
import os
import joblib

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings

from .models import UserInfo, Course, Enrollment

# Try to load ML model + mapping (fail-safe)
try:
    model = joblib.load(os.path.join(settings.BASE_DIR, 'myapp', 'model.pkl'))
except Exception:
    model = None

try:
    course_mapping = joblib.load(os.path.join(settings.BASE_DIR, 'myapp', 'course_mapping.pkl'))
except Exception:
    course_mapping = {}

def home(request):
    return HttpResponse("""
        <h1>Welcome!</h1>
        <a href="/login/">Login</a> | <a href="/register/">Register</a>
    """)

# Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if UserInfo.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'register.html')

        if UserInfo.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return render(request, 'register.html')

        UserInfo.objects.create(username=username, email=email, password=password)
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'register.html')

# Login
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = UserInfo.objects.get(email=email, password=password)
            request.session['username'] = user.username
            return redirect('success')
        except UserInfo.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, 'login.html')

    return render(request, 'login.html')

# Helper: skill mapping
def skill_level_to_numeric(skill):
    mapping = {'Beginner': 0, 'Intermediate': 1, 'Expert': 2}
    return mapping.get(skill, 0)

# Helper: Map ML indices -> Course model objects (robust matching)
def _map_indices_to_course_objects(indices):
    results = []
    # protect if course_mapping is a list / dict / other
    for idx in indices:
        mapped = None
        try:
            if isinstance(course_mapping, dict):
                mapped = course_mapping.get(idx)
            else:
                # attempt list-like access
                mapped = course_mapping[idx]
        except Exception:
            mapped = None

        course_obj = None

        # If mapping is an ID => fetch by id
        if isinstance(mapped, int):
            course_obj = Course.objects.filter(id=mapped).first()

        # If mapping is string => try exact title match then contains
        if not course_obj and isinstance(mapped, str):
            mapped_clean = mapped.strip()
            course_obj = Course.objects.filter(title__iexact=mapped_clean).first()
            if not course_obj:
                course_obj = Course.objects.filter(title__icontains=mapped_clean[:40]).first()

        # As a fallback, maybe the idx itself is a title (string)
        if not course_obj:
            try:
                if isinstance(idx, str):
                    idx_clean = idx.strip()
                    course_obj = Course.objects.filter(title__iexact=idx_clean).first()
                    if not course_obj:
                        course_obj = Course.objects.filter(title__icontains=idx_clean[:40]).first()
            except Exception:
                pass

        if course_obj:
            results.append(course_obj)
    return results

# Success (dashboard)
def login_success(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = UserInfo.objects.get(username=username)

    # ✅ ADDED: Handle Profile Form Submission
    # This allows you to save the details when the user clicks "Submit"
    if request.method == 'POST':
        user.phone_number = request.POST.get('phone_number')
        user.country = request.POST.get('country')
        user.city = request.POST.get('city')
        user.skill_level = request.POST.get('skill_level')
        # Handle scores safely (convert to int if present)
        m_score = request.POST.get('math_score')
        p_score = request.POST.get('programming_score')
        user.math_score = int(m_score) if m_score else 0
        user.programming_score = int(p_score) if p_score else 0
        
        user.field_of_study = request.POST.get('field_of_study')
        user.address = request.POST.get('address')
        
        user.save()
        messages.success(request, "Profile updated successfully!")
        
        # Reload the page to show recommendations now that profile is filled
        return redirect('success')

    # Check profile completeness
    profile_filled = any([
        user.phone_number,
        user.country,
        user.city,
        user.skill_level,
        user.math_score is not None,
        user.programming_score is not None,
        user.field_of_study,
        user.address
    ])

    recommended_courses = []

    # Only run ML when model & course_mapping exist and profile + interest present
    if profile_filled and user.interest and model is not None and course_mapping:
        skill_map = {'Beginner': 0, 'Intermediate': 1, 'Expert': 2}
        skill_level_encoded = skill_map.get(user.skill_level, 0)

        ai_interest = 1 if user.interest.lower() == "ai" else 0
        web_interest = 1 if user.interest.lower() == "web" else 0

        user_input = [
            skill_level_encoded,
            user.math_score or 0,
            user.programming_score or 0,
            ai_interest,
            web_interest
        ]

        try:
            proba = model.predict_proba([user_input])[0]
            sorted_indices = proba.argsort()[::-1]
            top_8_indices = sorted_indices[:8]  # ✅ now top 8

            # Map the ML top indices to Course objects (DB)
            recommended_courses = _map_indices_to_course_objects(top_8_indices)

        except Exception as e:
            print("Recommendation error:", e)
            recommended_courses = []

    # If no recommendations from ML, just show 8 fallback courses
    if not recommended_courses:
        recommended_courses = list(Course.objects.all()[:8])

    return render(request, 'success.html', {
        'username': username,
        'user': user,
        'profile_filled': profile_filled,
        'recommended_courses': recommended_courses
    })


# Interest selection (similar mapping to courses)
def interest_selection(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = UserInfo.objects.get(username=username)

    if request.method == "POST":
        interest = request.POST.get('interest')
        user.interest = interest
        user.save()
        messages.success(request, f"Interest saved: {interest}")

        # Prepare input
        skill_num = skill_level_to_numeric(user.skill_level)
        math_score = user.math_score if user.math_score else 0
        prog_score = user.programming_score if user.programming_score else 0
        ai_interest = 1 if interest.lower() == 'ai' else 0
        web_interest = 1 if interest.lower() == 'web' else 0

        user_input = [skill_num, math_score, prog_score, ai_interest, web_interest]

        recommended_courses = []
        if model is not None and course_mapping:
            try:
                proba = model.predict_proba([user_input])[0]
                sorted_indices = proba.argsort()[::-1]
                top_5_indices = sorted_indices[:5]
                recommended_courses = _map_indices_to_course_objects(top_5_indices)
            except Exception:
                recommended_courses = []

        return render(request, 'success.html', {
            'username': username,
            'user': user,
            'profile_filled': True,
            'recommended_courses': recommended_courses
        })

    return render(request, 'interest.html', {'user': user})

# All courses page -> use DB now (not course_mapping)
def all_courses_view(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = UserInfo.objects.get(username=username)
    courses = Course.objects.all()

    return render(request, 'all_courses.html', {
        'courses': courses,
        'user': user
    })

# Course detail + enroll
def course_detail_view(request, course_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = UserInfo.objects.get(username=username)
    course = get_object_or_404(Course, id=course_id)
    enrolled = Enrollment.objects.filter(user=user, course=course).exists()

    return render(request, 'course_detail.html', {
        'course': course,
        'user': user,
        'enrolled': enrolled
    })

def enroll_course_view(request, course_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = UserInfo.objects.get(username=username)
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)

    if created:
        messages.success(request, f"You have successfully enrolled in {course.title}!")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")

    return redirect('course_detail', course_id=course.id)

# Logout
@csrf_exempt
def logout_view(request):
    request.session.flush()
    return redirect('login')
