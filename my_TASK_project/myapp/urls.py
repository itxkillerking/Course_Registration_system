from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # root URL goes to login
    path('register/', views.register_view, name='register'),
    path('success/', views.login_success, name='success'),
    path('interest/', views.interest_selection, name='interest_selection'),
    path('all-courses/', views.all_courses_view, name='all_courses'),
    path('course/<int:course_id>/',  views.course_detail_view, name='course_detail'),  # ✅ course detail page
    path('course/<int:course_id>/enroll/', views.enroll_course_view, name='enroll_course'),  # ✅ enroll action
    path('logout/', views.logout_view, name='logout'),
]
