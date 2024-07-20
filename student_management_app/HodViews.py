from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import AddStudentForm, EditStudentForm

from .models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport


def admin_home(request):
    print("apun sbka baap h")
    print(request.user.user_type)
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')




def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        # messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


# def add_student(request):
#     form = AddStudentForm()
#     context = {
#         "form": form
#     }
#     return render(request, 'hod_template/add_student_template.html', context)




# def add_student_save(request):
#     if request.method != "POST":
#         messages.error(request, "Invalid Method")
#         return redirect('add_student')
#     else:
#         form = AddStudentForm(request.POST, request.FILES)
#         print("inside else")

#         print(form)
#         first_name = request.POST['first_name']
#         last_name = request.POST['last_name']
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         address = request.POST['address']
#         session_year_id = request.POST['session_year_id']
#         course_id = request.POST['course_id']
#         gender = request.POST['gender']

#         if len(request.FILES) != 0:
#             profile_pic = request.FILES['profile_pic']
#             fs = FileSystemStorage()
#             filename = fs.save(profile_pic.name, profile_pic)
#             profile_pic_url = fs.url(filename)
#         else:
#             profile_pic_url = None


#         try:
#             user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
#             user.students.address = address

#             course_obj = Courses.objects.get(id=course_id)
#             user.students.course_id = course_obj

#             session_year_obj = SessionYearModel.objects.get(id=session_year_id)
#             user.students.session_year_id = session_year_obj

#             user.students.gender = gender
#             user.students.profile_pic = profile_pic_url
#             user.save()
#             messages.success(request, "Student Added Successfully!")
#             return redirect('add_student')
#         except:
#             messages.error(request, "Failed to Add Student!")
#             return redirect('add_student')


# def manage_student(request):
#     students = Students.objects.all()
#     context = {
#         "students": students
#     }
#     return render(request, 'hod_template/manage_student_template.html', context)


# def edit_student(request, student_id):
#     # Adding Student ID into Session Variable
#     request.session['student_id'] = student_id
#     student = Students.objects.get(admin_id=student_id)
#     print
#     form = EditStudentForm()
#     # Filling the form with Data from Database
#     form.fields['email'].initial = student.admin.email
#     form.fields['username'].initial = student.admin.username
#     form.fields['first_name'].initial = student.admin.first_name
#     form.fields['last_name'].initial = student.admin.last_name
#     form.fields['address'].initial = student.address
#     form.fields['course_id'].initial = student.course_id.id
#     form.fields['gender'].initial = student.gender
#     form.fields['session_year_id'].initial = student.session_year_id.id

#     context = {
#         "id": student_id,
#         "username": student.admin.username,
#         "form": form
#     }
#     return render(request, "hod_template/edit_student_template.html", context)


# def edit_student_save(request):
#     if request.method != "POST":
#         return HttpResponse("Invalid Method!")
#     else:
#         student_id = request.session.get('student_id')
#         if student_id == None:
#             return redirect('/manage_student')

#         form = EditStudentForm(request.POST, request.FILES)
#     # if form.is_valid():
#         email = request.POST.get('email')
#         username = request.POST.get('username')
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         address = request.POST.get('address')
#         course_id = request.POST.get('course_id')
#         gender = request.POST.get('gender')
#         session_year_id = request.POST.get('session_year_id')
#         if len(request.FILES) != 0:
#             profile_pic = request.FILES['profile_pic']
#             fs = FileSystemStorage()
#             filename = fs.save(profile_pic.name, profile_pic)
#             profile_pic_url = fs.url(filename)
#         else:
#             profile_pic_url = None

#         try:
            
#             # First Update into Custom User Model
#             user = CustomUser.objects.get(id=student_id)
#             user.first_name = first_name
#             user.last_name = last_name
#             user.email = email
#             user.username = username
#             user.save()

#             # Then Update Students Table
#             student_model = Students.objects.get(admin=student_id)
#             student_model.address = address

#             course = Courses.objects.get(id=course_id)
#             student_model.course_id = course

#             session_year_obj = SessionYearModel.objects.get(id=session_year_id)
#             student_model.session_year_id = session_year_obj

#             student_model.gender = gender
#             if profile_pic_url != None:
#                 student_model.profile_pic = profile_pic_url
#             student_model.save()
#             # Delete student_id SESSION after the data is updated
#             del request.session['student_id']

#             messages.success(request, "Student Updated Successfully!")
#             return redirect('/edit_student/'+student_id)
#         except:
#             messages.success(request, "Failed to Uupdate Student.")
#             return redirect('/edit_student/'+student_id)
#     # else:
#             return redirect('/edit_student/'+student_id)


# def delete_student(request, student_id):
#     student = Students.objects.get(admin=student_id)
#     try:
#         student.delete()
#         messages.success(request, "Student Deleted Successfully.")
#         return redirect('manage_student')
#     except:
#         messages.error(request, "Failed to Delete Student.")
#         return redirect('manage_student')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from .models import CustomUser, Courses, Students, SessionYearModel, FeesStructure,StudentFees
from .forms import AddStudentForm, EditStudentForm,FeesStructure

def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)

def add_student_save(request):
    print("inside the add_srunet_save")
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)
        print("Form data:",form)
        if form.is_valid():
            try:
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                address = form.cleaned_data['address']
                session_year_id = form.cleaned_data['session_year_id']
                course_id = form.cleaned_data['course_id']
                gender = form.cleaned_data['gender']
                fees_structure = form.cleaned_data['fees_structure']

                if request.FILES.get('profile_pic'):
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage()
                    filename = fs.save(profile_pic.name, profile_pic)
                    profile_pic_url = fs.url(filename)
                else:
                    profile_pic_url = None

                    user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                    user.students.address = address
                    user.students.course_id = Courses.objects.get(id=course_id)
                    user.students.session_year_id = SessionYearModel.objects.get(id=session_year_id)
                    user.students.gender = gender
                    user.students.profile_pic = profile_pic_url
                    user.students.fees_structure = fees_structure
                    user.save()
                    messages.success(request, "Student Added Successfully!")
                    return redirect('add_student')
            except Exception as e:
                messages.error(request, f"Failed to Add Student: {str(e)}")
                return redirect('add_student')
        else:
            messages.error(request, "Form is not valid. Please check the entries.")
            return redirect('add_student')

def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)

def edit_student(request, student_id):
    student = get_object_or_404(Students, admin_id=student_id)
    form = EditStudentForm(initial={
        "email": student.admin.email,
        "username": student.admin.username,
        "first_name": student.admin.first_name,
        "last_name": student.admin.last_name,
        "address": student.address,
        "course_id": student.course_id.id,
        "gender": student.gender,
        "session_year_id": student.session_year_id.id,
        "fees_structure": student.fees_structure.id if student.fees_structure else None,
    })
    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form,
        "fees_structure": student.fees_structure.id if student.fees_structure else None,  # Handle potential None values
    }
    return render(request, "hod_template/edit_student_template.html", context)

def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.POST.get('student_id')
        if not student_id:
            return redirect('manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']
            fees_structure = form.cleaned_data['fees_structure']

            if request.FILES.get('profile_pic'):
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                student_model = Students.objects.get(admin=student_id)
                student_model.address = address
                student_model.course_id = Courses.objects.get(id=course_id)
                student_model.session_year_id = SessionYearModel.objects.get(id=session_year_id)
                student_model.gender = gender
                student_model.fees_structure = fees_structure
                if profile_pic_url:
                    student_model.profile_pic = profile_pic_url
                student_model.save()

                messages.success(request, "Student Updated Successfully!")
                return redirect('edit_student', student_id=student_id)
            except Exception as e:
                messages.error(request, f"Failed to Update Student: {str(e)}")
                return redirect('edit_student', student_id=student_id)
        else:
            messages.error(request, "Form is not valid. Please check the entries.")
            return redirect('edit_student', student_id=student_id)

def delete_student(request, student_id):
    student = get_object_or_404(Students, admin=student_id)
    try:
        student.admin.delete()  # This will also delete the associated Students object
        messages.success(request, "Student Deleted Successfully.")
    except Exception as e:
        messages.error(request, f"Failed to Delete Student: {str(e)}")
    return redirect('manage_student')


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            


def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

   
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def staff_profile(request):
    pass


def student_profile(requtest):
    pass



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import FeesStructure, TimeTable
from .forms import FeesStructureForm, TimeTableForm

def manage_fees(request):
    fees = FeesStructure.objects.all()
    return render(request, 'hod_template/manage_fees.html', {'fees': fees})

def add_fees(request):
    if request.method == 'POST':
        form = FeesStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fees structure added successfully')
            return redirect('manage_fees')
    else:
        form = FeesStructureForm()
    return render(request, 'hod_template/add_fees.html', {'form': form})

def edit_fees(request, pk):
    fees = get_object_or_404(FeesStructure, pk=pk)
    if request.method == 'POST':
        form = FeesStructureForm(request.POST, instance=fees)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fees structure updated successfully')
            return redirect('manage_fees')
    else:
        form = FeesStructureForm(instance=fees)
    return render(request, 'hod_template/edit_fees.html', {'form': form})

def delete_fees(request, pk):
    fees = get_object_or_404(FeesStructure, pk=pk)
    fees.delete()
    messages.success(request, 'Fees structure deleted successfully')
    return redirect('manage_fees')

def manage_timetable(request):
    timetable = TimeTable.objects.all()
    return render(request, 'hod_template/manage_timetable.html', {'timetable': timetable})

def add_timetable(request):
    if request.method == 'POST':
        form = TimeTableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry added successfully')
            return redirect('manage_timetable')
    else:
        form = TimeTableForm()
    return render(request, 'hod_template/add_timetable.html', {'form': form})

def edit_timetable(request, pk):
    timetable = get_object_or_404(TimeTable, pk=pk)
    if request.method == 'POST':
        form = TimeTableForm(request.POST, instance=timetable)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry updated successfully')
            return redirect('manage_timetable')
    else:
        form = TimeTableForm(instance=timetable)
    return render(request, 'hod_template/edit_timetable.html', {'form': form})

def delete_timetable(request, pk):
    timetable = get_object_or_404(TimeTable, pk=pk)
    timetable.delete()
    messages.success(request, 'Timetable entry deleted successfully')
    return redirect('manage_timetable')

from django.http import JsonResponse
from .models import Students, StudentFees
from django.db import models
from django.db.models import Sum
    # query = request.GET.get('q')
    # if query:
    #     students = Students.objects.filter(
    #         models.Q(admin__username__icontains=query) | 
    #         models.Q(admin__first_name__icontains=query) | 
    #         models.Q(admin__last_name__icontains=query)
    #     )

    #     context = {
    #         'students': students,
    #         'query':query
    #     }
    #     return render(request, 'hod_template/process_payment.html', context)
    # else:
       
    #     return render(request, 'hod_template/process_payment.html', {'students': []}) 
# def hod_search_students(request):

#     query = request.GET.get('q', '')
#     students = Students.objects.filter(admin__username__icontains=query) | Students.objects.filter(admin__first_name__icontains=query) | Students.objects.filter(admin__last_name__icontains=query)
    
#     # Adding calculated fields for each student
#     student_list = []
#     for student in students:
#         paid_fees = StudentFees.objects.filter(student_id=student.id).aggregate(Sum('paid_fees'))['paid_fees__sum'] or 0
#         due_fees = student.fees  - paid_fees
#         student_list.append({
#             'id': student.id,
#             'admin': student.admin,
#             'course_id': student.course_id,
#             'fees': student.fees,
#             'paid_fees': paid_fees,
#             'due_fees': due_fees
#         })

#     return render(request, 'hod_template/student_pay_fees.html', {'students': student_list})
    
# from django.db.models import Sum
# from .models import Students, StudentFees

# def hod_search_students(request):
#     query = request.GET.get('q', '')
#     students = Students.objects.filter(admin__username__icontains=query) | \
#                Students.objects.filter(admin__first_name__icontains=query) | \
#                Students.objects.filter(admin__last_name__icontains=query)

#     student_list = []
#     for student in students:
#         # Fetch StudentFees related to the student
#         try:
#             student_fees = StudentFees.objects.get(student=student)
#             paid_fees = student_fees.paid_fees
#         except StudentFees.DoesNotExist:
#             paid_fees = 0

#         # Calculate due fees based on fees structure
#         if student.fees_structure:
#             total_fees = student.fees_structure.total_fee
#         else:
#             total_fees = 0
        
#         due_fees = total_fees - paid_fees
        
#         student_list.append({
#             'id': student.id,
#             'admin': student.admin,
#             'course_id': student.course_id,
#             'fees': total_fees,  # Display total fees from fees_structure
#             'paid_fees': paid_fees,
#             'due_fees': due_fees
#         })

#     return render(request, 'hod_template/student_pay_fees.html', {'students': student_list})
    
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Students, StudentFees
# from django.contrib import messages

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, id=student_id)
#     student_fees = get_object_or_404(StudentFees, student=student) 

#     if request.method == 'POST':
#         amount_paid = int(request.POST.get('amount_paid', 0))
        
#         if amount_paid > 0:
#             student_fees.paid_fees += amount_paid
#             student_fees.save()
#             messages.success(request, 'Payment processed successfully!')
#         else:
#             messages.error(request, 'Invalid payment amount.')

#         return redirect('hod_search_students')

#     context = {
#         'student': student,
#         'student_fees': student_fees,
#     }
#     return render(request, 'hod_template/process_payment.html', context)
# def process_payment(request, student_id):
#     student = get_object_or_404(Students, id=student_id)
#     student_fees = get_object_or_404(StudentFees, student=student)

#     if request.method == 'POST':
#         amount_paid = int(request.POST.get('amount_paid', 0))
#         if amount_paid > 0:
#             student_fees.paid_fees += amount_paid
#             student_fees.save()
#             messages.success(request, 'Payment processed successfully!')
#         else:
#             messages.error(request, 'Invalid payment amount.')

#         return redirect('hod_search_students')

#     context = {
#         'student': student,
#         'student_fees': student_fees,
#     }
#     return render(request, 'hod_template/process_payment.html', context)

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Students, StudentFees

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, id=student_id)
#     student_fees = StudentFees.objects.filter(student_id=student).first()

#     if request.method == "POST":
#         amount_paid = int(request.POST['amount_paid'])

#         if student_fees:
#             student_fees.paid_fees += amount_paid
#             student_fees.save()
#         else:
#             StudentFees.objects.create(student_id=student.id, paid_fees=amount_paid)

#         messages.success(request, "Payment processed successfully!")
#         return redirect('hod_search_students')

#     context = {
#         'student': student,
#         'student_fees': student_fees,
#     }
#     return render(request, 'hod_template/process_payment.html', context)
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Students, StudentFees

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, id=student_id)
#     student_fees = StudentFees.objects.filter(student=student).first()

#     if request.method == "POST":
#         amount_paid = int(request.POST['amount_paid'])

#         if student_fees:
#             student_fees.paid_fees += amount_paid
#             student_fees.save()
#         else:
#             StudentFees.objects.create(student=student, paid_fees=amount_paid)

#         messages.success(request, "Payment processed successfully!")
#         return redirect('hod_search_students')

#     # Calculate total, paid, and due fees
#     total_fees = student_fees.total_fees if student_fees else 0
#     paid_fees = student_fees.paid_fees if student_fees else 0
#     due_fees = max(total_fees - paid_fees, 0)  # Ensure due fees is not negative

#     context = {
#         'student': student,
#         'student_fees': student_fees,
#         'total_fees': total_fees,
#         'paid_fees': paid_fees,
#         'due_fees': due_fees,
#     }
#     return render(request, 'hod_template/process_payment.html', context)



# views.py

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Students, StudentFees

# def student_detail(request, student_id):
#     student = get_object_or_404(Students, pk=student_id)
#     student_fees = student.studentfees  # Assuming OneToOneField relation
#     context = {
#         'student': student,
#         'student_fees': student_fees,
#     }
#     return render(request, 'dashboard/student_detail.html', context)

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, pk=student_id)
#     student_fees = student.studentfees  # Assuming OneToOneField relation

#     if request.method == 'POST':
#         amount_to_pay = float(request.POST.get('amount', 0))

#         if amount_to_pay <= 0:
#             messages.error(request, 'Invalid payment amount.')
#             return redirect('student_detail', student_id=student_id)

#         if student_fees.paid_fees + amount_to_pay > student_fees.total_fees:
#             messages.error(request, 'Payment amount exceeds total fees.')
#             return redirect('student_detail', student_id=student_id)

#         # Update student fees
#         student_fees.paid_fees += amount_to_pay
#         student_fees.save()

#         messages.success(request, 'Payment successful.')
#         return redirect('student_detail', student_id=student_id)

#     context = {
#         'student': student,
#         'student_fees': student_fees,
#     }
#     return render(request, 'dashboard/process_payment.html', context)


# # views.py

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import StudentFees

# def pay_fees(request):
#     if request.method == 'POST':
#         # Assuming you have a form to process payments
#         # Retrieve the student's fees instance
#         student_fees = StudentFees.objects.get(student__admin=request.user)
        
#         # Process payment logic here
#         # For simplicity, let's assume the payment updates the `paid_fees` field
#         amount_paid = float(request.POST.get('amount_paid', 0))
#         student_fees.paid_fees += amount_paid
#         student_fees.save()
        
#         # Optionally, you can add success messages or redirect to a success page
#         messages.success(request, f'Payment of {amount_paid} successfully processed.')
#         return redirect('pay_fees')  # Redirect to avoid form resubmission on refresh

#     # Fetch the student's fees instance for displaying current details
#     student_fees = StudentFees.objects.get(student__admin=request.user)
    
#     context = {
#         'student_fees': student_fees,
#     }
#     return render(request, 'fees/pay_fees.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Students, StudentFees
from .forms import SearchStudentForm

# def hod_search_students(request):
#     if request.method == 'GET':
#         form = SearchStudentForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data.get('query')
#             # Perform search logic based on username or name, assuming you have a search method
#             students = Students.objects.filter(admin__username__icontains=query) | \
#                        Students.objects.filter(admin__first_name__icontains=query) | \
#                        Students.objects.filter(admin__last_name__icontains=query)
#             for student in students:
#                 # Get total paid fees for the student
#                 total_paid_fees = StudentFees.objects.filter(student=student).aggregate(total_paid=Sum('paid_fees'))['total_paid'] or 0
#                 # Calculate due fees
#                 student.due_fees = student.total_fees - total_paid_fees
#             print(student.due_fees)

#             return render(request, 'hod_template/student_pay_fees.html', {'students': students, 'form': form})
#     else:
#         form = SearchStudentForm()

#     return render(request, 'hod_template/student_pay_fees.html', {'form': form})

from django.db.models import Sum

# def hod_search_students(request):
#     form = SearchStudentForm(request.GET or None)
#     students = []

#     if request.method == 'GET':
#         if form.is_valid():
#             query = form.cleaned_data.get('query')
#             # Perform search logic based on username or name
#             students = Students.objects.filter(admin__username__icontains=query) | \
#                        Students.objects.filter(admin__first_name__icontains=query) | \
#                        Students.objects.filter(admin__last_name__icontains=query)

#     # Calculate due fees for each student
#     print(students)
#     for student in students:
#         print(student.total_fees)
#         # Get total paid fees for the student
#         total_paid_fees = StudentFees.objects.filter(student=student).aggregate(total_paid=Sum('paid_fees'))['total_paid'] or 0
#         print(total_paid_fees)
#         due_fees = student.total_fees - total_paid_fees

#     return render(request, 'hod_template/student_pay_fees.html', {'students': students, 'form': form,'due_fees':due_fees,'total_paid_fees':total_paid_fees})
def hod_search_students(request):
    form = SearchStudentForm(request.GET or None)
    students = []
    due_fees_dict = {}
    total_paid_fees_dict = {}

    if request.method == 'GET':
        if form.is_valid():
            query = form.cleaned_data.get('query')
            # Perform search logic based on username or name
            students = Students.objects.filter(admin__username__icontains=query) | \
                       Students.objects.filter(admin__first_name__icontains=query) | \
                       Students.objects.filter(admin__last_name__icontains=query)

    # Calculate due fees for each student
    for student in students:
        total_paid_fees = StudentFees.objects.filter(student=student).aggregate(total_paid=Sum('paid_fees'))['total_paid'] or 0
        due_fees = student.total_fees - total_paid_fees
        due_fees_dict[student.id] = due_fees
        total_paid_fees_dict[student.id] = total_paid_fees

    return render(request, 'hod_template/student_pay_fees.html', {
        'students': students,
        'form': form,
        'due_fees_dict': due_fees_dict,
        'total_paid_fees_dict': total_paid_fees_dict
    })

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, pk=student_id)
#     student_fees = get_object_or_404(StudentFees, student=student)
#     print(student_fees.paid_fees)
#     if request.method == 'POST':
#         amount_paid = float(request.POST.get('amount_paid'))
#         student_fees.paid_fees += amount_paid
#         student_fees.due_fees -= amount_paid
#         student_fees.save()
#         return redirect(reverse('student_detail', args=[student_id]))

#     return render(request, 'hod_template/process_payment.html', {'student': student, 'student_fees': student_fees})

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Students, StudentFees
from .forms import SearchStudentForm

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, pk=student_id)
#     student_fees = get_object_or_404(StudentFees, student=student)
    
#     if request.method == 'POST':
#         student_fees = FeesStructure.objects.get(course= student.course_id)
#         paid = Students.objects.get(pk = student_id)
#         amount_paid = float(request.POST.get('amount_paid'))
#         if paid.paid_fees + amount_paid > student_fees.total_fee:
#             amount_paid = student_fees.total_fee - paid.paid_fees
#         paid.paid_fees = paid.paid_fees + amount_paid
#         print("inside the request method the poadi fees is ",paid.paid_fees)
#         paid.save()
#         return redirect(reverse('process_payment', args=[student_id]))

#     student_fees = FeesStructure.objects.get(course= student.course_id)
#     print("Snsjfkdkhdfkg",student_fees.total_fee)
#     paid = get_object_or_404(Students,pk = student_id)
#     due_fees = student_fees.total_fee - paid.paid_fees
#     print(due_fees)
#     return render(request, 'hod_template/process_payment.html', {'student': student, 'student_fees': student_fees,'paid': paid,'due_fees' : due_fees})

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import Students, StudentFees, FeesStructure

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, pk=student_id)
    
#     if request.method == 'POST':
#         course_fee = FeesStructure.objects.get(course=student.course_id)
#         amount_paid = float(request.POST.get('amount_paid'))
        
#         student_fees, created = StudentFees.objects.get_or_create(student=student)
        
#         if student_fees.paid_fees + amount_paid > course_fee.total_fee:
#             amount_paid = course_fee.total_fee - student_fees.paid_fees
        
#         student_fees.paid_fees += amount_paid
#         student_fees.save()
        
#         return redirect(reverse('process_payment', args=[student_id]))

#     course_fee = FeesStructure.objects.get(course=student.course_id)
#     student_fees, created = StudentFees.objects.get_or_create(student=student)
#     due_fees = course_fee.total_fee - student_fees.paid_fees
    
#     return render(request, 'hod_template/process_payment.html', {'student': student, 'student_fees': course_fee, 'paid': student_fees, 'due_fees': due_fees})


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Students, FeesStructure, StudentFees

# def process_payment(request, student_id):
#     student = get_object_or_404(Students, pk=student_id)
    
#     if request.method == 'POST':
#         amount_paid = float(request.POST.get('amount_paid'))
        
#         student_fees, created = StudentFees.objects.get_or_create(student=student)
#         course_fee = student.total_fees
        
#         if student_fees.paid_fees + amount_paid > course_fee:
#             amount_paid = course_fee - student_fees.paid_fees
        
#         student_fees.paid_fees += amount_paid
#         student_fees.save()
        
#         return redirect(reverse('process_payment', args=[student_id]))

#     course_fee = student.total_fees
#     student_fees, created = StudentFees.objects.get_or_create(student=student)
#     due_fees = course_fee - student_fees.paid_fees
    
#     return render(request, 'hod_template/process_payment.html', {
#         'student': student,
#         'student_fees': student_fees,
#         'course_fee': course_fee,
#         'due_fees': due_fees
#     })


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from decimal import Decimal
from .models import Students, StudentFees

def process_payment(request, student_id):
    student = get_object_or_404(Students, pk=student_id)
    
    if request.method == 'POST':
        amount_paid = Decimal(request.POST.get('amount_paid', '0.0'))
        
        student_fees, created = StudentFees.objects.get_or_create(student=student)
        
        student_fees.paid_fees += amount_paid
        student_fees.save()
        
        return redirect(reverse('process_payment', args=[student_id]))

    course_fee = student.total_fees
    total_paid_fees = StudentFees.objects.filter(student=student).aggregate(total_paid=Sum('paid_fees'))['total_paid'] or Decimal('0.0')
    due_fees = student.total_fees - total_paid_fees
    
    return render(request, 'hod_template/process_payment.html', {'student': student, 'due_fees': due_fees, 'total_paid_fees': total_paid_fees, 'course_fee': course_fee})

from django.shortcuts import render, get_object_or_404
from .models import Students, StudentFees

def student_detail(request, student_id):
    student = get_object_or_404(Students, pk=student_id)
    student_fees, created = StudentFees.objects.get_or_create(student=student)
    due_fees = student.total_fees - student_fees.paid_fees
    
    return render(request, 'student_detail.html', {
        'student': student,
        'due_fees': due_fees,
        'student_fees': student_fees,
    })