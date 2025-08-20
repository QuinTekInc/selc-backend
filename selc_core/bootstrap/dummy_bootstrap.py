

"""
THIS BOOTRSTAP FILE IS USED FOR POPULATING DUMMY DATA
NOTE: This is meant to be used only during testing and not in production
"""


from .bootstrap_constants import dummy_departments_data, dummy_lecturers_data, dummy_students_data
from .bootstrap_constants import dummy_courses_data, dummy_class_courses
from .bootstrap import populate_groups_and_permissions, populate_categories_and_questions
from selc_core.models import *
from django.contrib.auth.models import User, Group


def splitName(full_name: str) ->tuple:
    name_split = full_name.split(' ')
    return name_split[0], ' '.join(name_split[1: len(name_split)])


def checkDepartment(dept_name: str) -> Department:
    departments = list(Department.objects.all())

    departments = filter(lambda dept: dept.department_name.lower() == dept_name.lower(), departments)

    if len(departments) == 0:
        return None
    

    return departments[0]




def popluateDummyDepartments():

    for dept_name in dummy_departments_data:
        department = Department.objects.create(department_name=dept_name)
        department.save()

    pass





def populateDummyLecturers():

    for dummy_lecturer in dummy_lecturers_data:

        username = dummy_lecturer['username']
        first_name, last_name = splitName(dummy_lecturer['name'])
        email = dummy_lecturer['email']

        users = User.objects.filter(username=username)

        user = None

        if users.exists():
            action = input(f'Username, {username} already exists. would you want to update with incoming data?[y/n]')

            if action.lower() == 'n':
                continue

            user = users.first()

        else:
            print(f'CREATING LECTURER, {username}')
            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            user.set_password('password')
            pass



        group = Group.objects.get(name='lecturer')
        user.groups.add(group)
        
        user.save()

        department_name = dummy_lecturer['department']

        lecturer = Lecturer.objects.create(user=user)


        department = checkDepartment(department_name)

        if not department or department is None:
            lecturer.save()
            print(f'Department, {department_name}, does not exist')
            continue

        lecturer.department = department
        lecturer.save()

    pass




def populateDummyCourses():

    print('POPULATING COURSES....')

    for dummy_course in dummy_courses_data:
        course_code = dummy_course['course_code']
        title = dummy_course['course_title']


        print(f'CREATING COURSE: {title}[{course_code}]')

        if Course.objects.filter(course_code=course_code).exists():
            print(f'COURSE, {course_code}, already exists.')
            continue

        course = Course.objects.create(course_code=course_code, title=title)
        course.save()

    print('POPULATION STATUS:.....DONE')

    pass



def populateDummyClassCourses():
    pass




def populateDummyStudents():

    for dummy_student in dummy_students_data:

        username = dummy_student['username']
        first_name, last_name = splitName(dummy_student['name'])
        program = dummy_student['program']
        reference_number = dummy_student['reference_number']

        department_name = dummy_student['department']


        user = User.objects.create( 
            username=username, 
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password('password')

        group = Group.objects.get(name='student')
        user.groups.add(group)


        user.save()


        student = Student.objects.create(
            user=user, 
            reference_number=reference_number, program=program,)

        depts = Department.objects.filter(department_name=department_name)

        if not depts.exists():
            student.save()
            continue

        department = depts.first()
        student.department = department

        student.save()

    pass




def initDummyDataPopulation():

    #some functions for the production bootstrap files
    populate_groups_and_permissions()
    populate_categories_and_questions()

    #first populate independent entities.

    popluateDummyDepartments()
    populateDummyCourses()

    populateDummyLecturers()
    populateDummyStudents()
    pass


