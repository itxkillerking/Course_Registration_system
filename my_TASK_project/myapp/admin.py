from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import UserInfo, Course, Enrollment  # ✅ Added Enrollment

@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = (
        'username', 
        'email', 
        'phone_number', 
        'country', 
        'city', 
        'skill_level', 
        'math_score', 
        'programming_score', 
        'field_of_study', 
        'address',
        'interest',
    )
    
    fields = (
        'username', 
        'email', 
        'password', 
        'phone_number', 
        'country', 
        'city', 
        'skill_level', 
        'math_score', 
        'programming_score', 
        'field_of_study', 
        'address',
        'interest',
    )

# ✅ Admin for Courses
@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = (
        'title', 'category', 'level', 'duration', 
        'instructor', 'price', 'language', 'grade'
    )
    search_fields = ('title', 'category', 'instructor')
    list_filter = ('category', 'level', 'language')

# ✅ Admin for Enrollments
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    list_filter = ('enrolled_at', 'course')
    search_fields = ('user__username', 'course__title')
