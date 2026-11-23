from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm
from .models import Student


def get_student_count(user):
    key = f'student_count_{user.id}'
    count = cache.get(key)
    if count is None:
        count = Student.objects.filter(created_by=user).count()
        cache.set(key, count, 300)
    return count


@login_required
def dashboard(request):
    students = Student.objects.filter(created_by=request.user)
    context = {
        'total_students': get_student_count(request.user),
        'total_departments': students.values('department').distinct().count(),
        'recent_students': students.order_by('-created_at')[:5],
    }
    return render(request, 'students/dashboard.html', context)


@login_required
def student_list(request):
    students = Student.objects.filter(created_by=request.user)

    query = request.GET.get('q', '')
    if query:
        students = students.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(department__icontains=query)
        )

    department = request.GET.get('department', '')
    if department:
        students = students.filter(department=department)

    paginator = Paginator(students.order_by('-created_at'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    departments = (
        Student.objects
        .filter(created_by=request.user)
        .values_list('department', flat=True)
        .distinct()
    )

    context = {
        'students': page_obj,
        'query': query,
        'department': department,
        'departments': departments,
    }
    return render(request, 'students/student_list.html', context)


@login_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if form.is_valid():
        student = form.save(commit=False)
        student.created_by = request.user
        student.save()
        messages.success(request, 'Student সফলভাবে যোগ হয়েছে।')
        return redirect('student_list')

    return render(request, 'students/student_form.html', {'form': form})


@login_required
def student_update(request, id):
    student = get_object_or_404(Student, id=id, created_by=request.user)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, 'তথ্য সফলভাবে আপডেট হয়েছে।')
        return redirect('student_list')

    return render(request, 'students/student_form.html', {'form': form})


@login_required
def student_delete(request, id):
    student = get_object_or_404(Student, id=id, created_by=request.user)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student মুছে ফেলা হয়েছে।')
        return redirect('student_list')

    return render(
        request,
        'students/student_confirm_delete.html',
        {'student': student},
    )


def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    context = {
        'total_students': Student.objects.filter(
            created_by=request.user
        ).count(),
    }
    return render(request, 'students/profile.html', context)
