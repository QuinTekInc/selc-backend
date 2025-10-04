

import pandas as pd


file_name = 'class_register.xlsx'
file_path = '~/Desktop/selc_backend/selc_core/bootstrap/'

df = pd.read_excel(f'{file_path}{file_name}')

#drop all rows where there is not value for the reference number
df = df.dropna(subset=['Reference Number'])

print(df.head())


def clean_reference_number(reference_number: str) -> str:
    new_ref = str(reference_number).strip()

    if ' ' in new_ref:
        new_ref = new_ref.replace(' ', '')
    
    if '-' in new_ref:
        new_ref = new_ref.replace('-','')

    start_with_clause = new_ref.startswith('UA') or new_ref.startswith('ua')
    
    #print(f'Start with UA: {start_with_clause}, ref: {new_ref}')

    if not start_with_clause:
        new_ref = 'UA' + new_ref

    return new_ref


def create_username(reference_number: str):
    username = 'UENR' + reference_number
    return username


df['clean_ref'] = df['Reference Number'].apply(clean_reference_number)
df['username'] = df['clean_ref'].apply(create_username)


def clean_first_name(first_name: str):
    if pd.isna(first_name):
        return ''
    
    return first_name.strip()



def clean_other_name(middle_name: str, last_name: str):
    other_names = ''

    if not pd.isna(middle_name):
        other_names += middle_name.strip() + ' '
    
    if not pd.isna(last_name):
        other_names += last_name.strip()

    return other_names


df['clean_first_name'] = df['First Name'].apply(clean_first_name)
df['clean_other_name'] = df.apply(lambda row: clean_other_name(row['Middle Name'], row['Last Name']), axis=1)


#create a new dataframe with the following columns:
#username, first_name, other_names, clean_ref(cleaneed reference number)
new_df = df[['username', 'First Name', 'clean_other_name', 'clean_ref']]

#rename the columns to username, first_name, other_names, reference_number
new_df = new_df.rename(columns={'First Name': 'first_name', 'clean_other_name': 'other_names', 'clean_ref': 'reference_number'})
#new_df.to_json('cleaned_students.json', indent=4, orient='records')


from django.contrib.auth.models import User, Group
from selc_core.models import *


# def createUserAccount(row):

#     username: str = row['username']
#     password: str = 'password'
#     fname: str = row['first_name']
#     onames: str = row['other_names']
#     ref_number: str = row['reference_number']


#     print('CREATE user', username)


#     users = User.objects.filter(username=username)

#     if  not users.exists():
#         #create the account
#         user = User.objects.create(username=username, first_name=fname, last_name=onames)
#         user.set_password(password)
        
#         #get the student group
#         group = Group.objects.get(name='student')
#         user.groups.add(group)

#         user.save()

#     else: 
#         user = users.first()

    
#     #create a Student object for the user

#     print('CREATING student ', ref_number)

#     students = Student.objects.filter(user=user)

#     if not students.exists():
#         student = Student.objects.create(user=user)
#         student.department = Department.objects.all().first()
#         student.reference_number = ref_number 
#         student.age = 21
#         student.program = "BSc. Computer Science"
#         student.save()
#     else:
#         student = students.first()

    
#     print('REGISTERING COURSES')
    
#     class_courses = ClassCourse.objects.filter(year=2025, semester=2)

#     #register the students for their class_courses
#     for class_course in class_courses:
#         student_classes = StudentClass.objects.filter(class_course=class_course, student=student)
        
#         if student_classes.exists():
#             continue 

#         student_class = StudentClass.objects.create(student=student, class_course=class_course)
#         student_class.save()
#         pass

#     print('\n\n')


#     pass




from django.contrib.auth.models import User, Group
from selc_core.models import *

def createUserAccount(row):
    username: str = row['username']
    password: str = 'password'
    fname: str = row['first_name']
    onames: str = row['other_names']
    ref_number: str = row['reference_number']

    print(f'Creating user: {username}')

    user, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': fname, 'last_name': onames}
    )

    if created:
        user.set_password(password)
        group = Group.objects.get(name='student')
        user.groups.add(group)
        user.save()
        print(f'User account created for {username}')
    else:
        print(f'User {username} already exists')

    # --- Create or get student record ---
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            'department': Department.objects.all().first(),
            'reference_number': ref_number,
            'age': 21,
            'program': "BSc. Computer Science",
        }
    )

    if created:
        print(f'Student record created: {ref_number}')
    else:
        print(f'Student {ref_number} already exists')

    # --- Register courses ---
    print('Registering courses...')
    class_courses = ClassCourse.objects.filter(year=2025, semester=2)

    for class_course in class_courses:
        StudentClass.objects.get_or_create(
            student=student,
            class_course=class_course
        )

    print('Done.\n')


# ✅ Apply to each row of your DataFrame
new_df.apply(createUserAccount, axis=1)


new_df.apply(createUserAccount, axis=1)