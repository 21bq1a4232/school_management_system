from django import forms
from .models import Courses, SessionYearModel,FeesStructure


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.CharField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@vvit'):
            raise forms.ValidationError("Email must end with 'VVIT' Domain")
        return email

    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    #For Displaying Courses
    try:
        courses = Courses.objects.all()
        course_list = []
        for course in courses:
            single_course = (course.id, course.course_name)
            course_list.append(single_course)
    except:
        print("here")
        course_list = []
    
    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []
    
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    course_id = forms.ChoiceField(label="Course", choices=course_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))
    fees_structure = forms.ModelChoiceField(label="Fees Structure", queryset=FeesStructure.objects.none(), widget=forms.Select(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        try:
            self.fields['course_id'].choices = [(course.id, course.course_name) for course in Courses.objects.all()]
            self.fields['session_year_id'].choices = [(session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year)) for session_year in SessionYearModel.objects.all()]
            self.fields['fees_structure'].queryset = FeesStructure.objects.all()
        except:
            self.fields['course_id'].choices = []
            self.fields['session_year_id'].choices = []
            self.fields['fees_structure'].queryset = FeesStructure.objects.none()



class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    try:
        courses = Courses.objects.all()
        course_list = []
        for course in courses:
            single_course = (course.id, course.course_name)
            course_list.append(single_course)
    except:
        course_list = []

    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []

    
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    course_id = forms.ChoiceField(label="Course", choices=course_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))
    fees_structure = forms.ModelChoiceField(label="Fees Structure", queryset=FeesStructure.objects.none(), widget=forms.Select(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        try:
            self.fields['course_id'].choices = [(course.id, course.course_name) for course in Courses.objects.all()]
            self.fields['session_year_id'].choices = [(session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year)) for session_year in SessionYearModel.objects.all()]
            self.fields['fees_structure'].queryset = FeesStructure.objects.all()
        except:
            self.fields['course_id'].choices = []
            self.fields['session_year_id'].choices = []
            self.fields['fees_structure'].queryset = FeesStructure.objects.none()
    
    
    
    
from django import forms
from .models import FeesStructure, TimeTable, Courses, Subjects, SessionYearModel

class FeesStructureForm(forms.ModelForm):
    class Meta:
        model = FeesStructure
        fields = ['course', 'session_year', 'tuition_fee']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'session_year': forms.Select(attrs={'class': 'form-control'}),
            'tuition_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'library_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'lab_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'other_fee': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = ['course', 'subject', 'day_of_week', 'start_time', 'end_time', 'room_number']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class SearchStudentForm(forms.Form):
    query = forms.CharField(label='Search Student')