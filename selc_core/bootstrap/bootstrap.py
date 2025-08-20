
from django.contrib.auth.models import Group, Permission
from selc_core.models import QuestionCategory, Questionnaire
from .bootstrap_constants import questions_and_categories, groups_and_permissions

#this the bootsrap for the file.



# def getCategoryNames() -> list[str]:
#     return [cat_dict['cat_name'] for cat_dict in questions_and_categories]



# populates the default categories and default questions to the database.
def populate_categories_and_questions():

    print('POPOULATING TABLES, QuestionCategory and Questionnaire')
    
    for cat_dict in questions_and_categories:
        #create the categories here.
        category_name = cat_dict['category']

        print(f'CREATING CATEGORY: {category_name}')

        #the category needs to be first created and save before it can be used with the questionnaire object.
        category = QuestionCategory.objects.create(cat_name=category_name)
        category.save()

        questions_dict: list[dict] = cat_dict['questions']

        for question_dict in questions_dict:
            question_text = question_dict['question']
            answer_type = question_dict['answer_type']

            questionnaire = Questionnaire.objects.create(
                question=question_text, answer_type=answer_type, category=category)
            questionnaire.save()

            pass
        
        print(f'Questionnaire population status.......DONE')

        pass




#populates the with the default groups
#this data has aleady been in popluated.
#this function has been already been populated throw the shell.
def populate_groups_and_permissions(): 

    print('POPULATE GROUPS AND PERMISSIONS')

    for group_dict in groups_and_permissions:
        group_name = group_dict['group']

        
        print(f'Creating group: {group_name}')


        groups = Group.objects.filter(name=group_name)
        
        if groups.exists():
            group = groups.first()
        else:
            group = Group.objects.create(name=group_name)

        if group_name == 'superuser':
            
            for _permission in Permission.objects.all():
                print(f'Enable permission: {_permission.codename}')
                group.permissions.add(_permission)
                pass

            group.save()
            print(f'CREATION_STATUS: {group_name} .... Done.')
            continue

        permission_code_names = group_dict['permissions']
        

        for p_code_name in permission_code_names:

            print(f'Enable permission: {p_code_name}')

            permission = Permission.objects.filter(codename=p_code_name)

            if not permission.exists():
                raise Exception(f'BootstrapException: Permission Code Name, {p_code_name}, does not exist.')
            
            group.permissions.add(permission.first())
            pass

        group.save()    
        print('CREATION_STATUS .....Done')
        pass

    pass




#todo: fetch lecturers data from the school's server
#updates are performed in the local server if necessary
def get_lecturers_data():
    pass




#todo: fetch student's data from the shool's main server
#updates to local database is performed when necessary
#data fetched are students who currently in admission
def get_students_data():
    pass




#todo: fetch courses data from the school's server
#updates to our local server is performed when necessary
def get_courses_data():
    pass



#todo: get all the courses assigned to the lecturers from the school's server
#updates to our local database is performed when necessary
#we use the data received to create ClassCourse objects in the database.
def get_class_courses():
    pass




#todo: get all the registered courses of students from the school's server
#updates to our local database are performed when necessary
#creates StudentClass objects with the data that will be received.
def get_students_registered_classes():
    pass

