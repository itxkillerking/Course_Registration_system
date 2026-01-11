from django.db import models

class UserInfo(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    
    # Profile fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    skill_level = models.CharField(max_length=20, blank=True, null=True)  # Beginner/Intermediate/Expert
    math_score = models.PositiveIntegerField(blank=True, null=True)        # % value
    programming_score = models.PositiveIntegerField(blank=True, null=True) # % value
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # New field for interest selection
    interest = models.CharField(max_length=50, blank=True, null=True)  # AI / Software / Others

    def __str__(self):
        return self.username
class Course(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.CharField(max_length=50)  # e.g., "6 weeks"
    instructor = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    language = models.CharField(max_length=50)
    grade = models.CharField(max_length=10, blank=True, null=True)  # Initially empty

    def __str__(self):
        return self.title
class Enrollment(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')  # prevents duplicate enrollments

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

