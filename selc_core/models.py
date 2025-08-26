
from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


import datetime

# Create your models here.


class Notification(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user: User = models.OneToOneField(User, null=False, on_delete=models.CASCADE) #whom the notification is meant for.
    title = models.CharField(max_length=300, default='')
    message = models.TextField(default='')
    read = models.BooleanField(default=False)

    def __repr__(self):
        return f'NOTIFICATION({self.id}, {self.user.username}, {self.title})'
    
    def __str__(self):
        return str(self.__repr__())
    
    def toMap(self):
        return {
            'id': self.id, 
            'title': self.title,
            'message': self.message,
            'read': self.read
        }





class GeneralSetting(models.Model):
    current_semester = models.IntegerField(default=1)
    enable_evaluations = models.BooleanField(default=False)

    def __repr__(self):
        return f'semester: {self.current_semester}', f'accept_evaluations: {self.enable_evaluations}'
    
    def __str__(self):
        return str(self.__repr__())
    
    def toMap(self) -> dict:
        return {
            'current_semester': self.current_semester,
            'enable_evaluations': self.enable_evaluations
        }





class Department(models.Model):

    id = models.BigAutoField(primary_key=True)
    department_name = models.CharField(max_length=120, unique=True, null=False)

    def __repr__(self):
        return self.id, self.department_name

    def __str__(self):
        return str(self.__repr__())

    def toMap(self):
        return {
            'department_id': self.id,
            'department_name': self.department_name
        }
    
    pass




#the student's information
class Student(models.Model):
    user = models.OneToOneField(User, null=False,  on_delete=models.CASCADE)
    reference_number = models.CharField(max_length=50, null=False)
    index_number = models.CharField(max_length=50, default='')
    age = models.IntegerField(default=18, null=False) #mostly people who come to the university are 18 years and above.
    department: Department = models.ForeignKey(Department, related_name='std_dept', null=True, on_delete=models.SET_NULL)
    program = models.CharField(max_length=100)
    campus = models.CharField(max_length=100, default='Sunyani')
    status = models.CharField(max_length=100, default='Regular')

    def __repr__(self):
        return self.user.username ,f'REF: {self.reference_number}',  self.age, self.program

    def __str__(self):
        return str(self.__repr__())
    

    def getRegisteredCourses(self) -> list:
        """
        This function returns a list of all the registered courses for a student 
        at the current instance studied in this current semester and academic year.
        """

        class_courses = ClassCourse.objects.filter(
            year = datetime.datetime.now().year,
            semester = GeneralSetting.objects.all().first().current_semester,
        )


        student_classes = []


        for class_course in class_courses:
            try:
                student_class = StudentClass.objects.get(student=self, class_course=class_course)
                student_classes.append(student_class)
            except StudentClass.DoesNotExist:
                continue

        return student_class
    

    def getFullName(self):
        return f'{self.user.first_name} {self.user.last_name}'


    def toMap(self):

        token, _ = Token.objects.get_or_create(user=self.user)
        
        return {
            'full_name': self.getFullName(),
            'index_number': self.index_number,
            'reference_number': self.reference_number,
            'department': self.department.department_name,
            'program': self.program,
            'age': self.age,
            'campus': self.campus,
            'status': self.status,
            'token': token.key
        }
    
    pass 




#the lecturers information
class Lecturer(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    department: Department = models.ForeignKey(Department, related_name='department', null=True, on_delete=models.SET_NULL)

    def getFullName(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'
    
    def getDepartmentName(self):
        if self.department:
            return self.department.department_name
        
        return None

    def __repr__(self):
        
        return self.user.username, self.getFullName(), self.getDepartmentName()

    
    def __str__(self):
        return str(self.__repr__())



    def computeLecturerOverallAverageRating(self) -> float:

        class_courses = ClassCourse.objects.filter(lecturer=self)

        if len(class_courses) == 0:
            return 0 
        
        total_ratings = 0
        
        for class_course in class_courses:
            lecturer_ratings = LecturerRating.objects.filter(class_course=class_course)
            total_ratings += sum([l_rating.rating for l_rating in lecturer_ratings])
        
        return total_ratings / len(class_courses)


    def toMap(self):

        return {
            'username': self.user.username,
            'name': f'{self.user.first_name} {self.user.last_name}',
            'email': self.user.email.strip() if self.user.email else 'N/A',
            'rating': self.computeLecturerOverallAverageRating(),
            'department': self.getDepartmentName(),
        }
    
    pass





#course information
class Course(models.Model):
    course_code = models.CharField(primary_key=True, max_length=20,  unique=True)
    title = models.CharField(max_length=200, default='')

    
    def __repr__(self):
        return self.course_code, self.title

    def __str__(self):
        return str(self.__repr__())



    #todo: this method calculates the cummulative performance rating and remarks of the course.
    #this calculation is based on the class_courses related to the current course.

    def computeMeanScore(self) -> float:

        #get all the class courses corresponding to this class.
        class_courses = ClassCourse.objects.filter(course=self)

        #the length of the class courses for this course in particular.
        total_evaluations = len(class_courses)

        if total_evaluations == 0:
            return 0
        
        #get the peformance score of each class_course, collect them to a list and find the sum
        total_score = sum([cc.computeGrandMeanScore() for cc in class_courses])

        #calculate the average and returns it.
        return total_score / total_evaluations



    def toMap(self):

        from .core_utils import getScoreRemark

        mean_score = self.computeMeanScore()

        remark = getScoreRemark(mean_score)

        return {
            'course_code': self.course_code,
            'course_title': self.title,
            'mean_score': mean_score, 
            'remark': remark
        }
    
    pass 





#the course to be studied for particular class 
class ClassCourse(models.Model):

    id = models.AutoField(primary_key=True)
    course: Course = models.ForeignKey(Course, related_name='cc_course', on_delete=models.CASCADE)
    credit_hours = models.IntegerField(default=3)
    lecturer: Lecturer = models.ForeignKey(Lecturer, related_name='lecturer', on_delete=models.CASCADE)
    semester = models.IntegerField(default=1)
    year = models.IntegerField(null=True)
    has_online = models.BooleanField(default=False)


    def computeLecturerRatingForCourse(self):
        ratings = LecturerRating.objects.filter(class_course=self)

        if len(ratings) == 0:
            return 0

        ratings_sum = sum([rating.rating for rating in ratings])

        return ratings_sum / len(ratings)


    #the mean score for the course.
    def computeGrandMeanScore(self) -> float:

        from .core_utils import ANSWER_SCORE_DICT

        #get all performance evaluations
        evaluations = Evaluation.objects.filter(class_course=self)

        total_evaluations = len(evaluations)

        if total_evaluations == 0:
            return 0
        
        ##filter the questionnaire answers where the answer_type to the question is "performance"

        # performance_evaluations = list(filter(
        #     lambda evaluation: evaluation.question.answer_type == 'performance', evaluations))

        #get the answers for the performance_evaluations for the this class_course, convert the answer to a value in the scale of 1-5, 
        #collect them a list and find the total sum of all the values.
        total_performance_score = sum(
            [ANSWER_SCORE_DICT.get(evaluation.answer, 0) for evaluation in evaluations])


        #compute the average and return it.
        return total_performance_score / total_evaluations
    


    def getEvalSuggestions(self) -> list[dict]:
        suggestions = EvaluationSuggestion.objects.filter(class_course=self)

        return [suggestion.toMap() for suggestion in suggestions]
    


    def getEvalDetails(self) -> list[dict]:

        from admin_api import utils

        #get the questions
        questions = Questionnaire.objects.all()

        eval_list = []


        for question in questions:

            #get the evaluations for the question at the current iteration
            evaluations = Evaluation.objects.filter(question=question, class_course=self)

            question_eval_dict = {
                'question': question.question,
                'answer_type': question.answer_type,
                'answer_summary': {

                }
            }


            total_evaluations = len(evaluations)
            max_answer_score = 5 * len(evaluations)
            total_answer_score = 0

            #build a set for the possible answers  for the question at the current iteration
            possible_question_answers: set[str] = set([evaluation.answer for evaluation in evaluations])

            for possible_answer in possible_question_answers: 
                answer_count = len(
                    list(filter(lambda evaluation: evaluation.answer==possible_answer, evaluations)))
                question_eval_dict['answer_summary'][possible_answer] = answer_count

                total_answer_score += utils.ANSWER_SCORE_DICT[possible_answer.lower()]

                pass

            
            #calculate the average answer score.
            percentage_score = (total_answer_score / max_answer_score) * 100
            average_answer_score = total_answer_score / total_evaluations



            #update the dictionary
            question_eval_dict['percentage_score'] = percentage_score
            question_eval_dict['average_score'] = average_answer_score
            question_eval_dict['remark'] = utils.categoryScoreBasedRemark(average_answer_score)
            

            eval_list.append(question_eval_dict)

            pass 

        return eval_list



    def getEvalQuestionCategoryRemarks(self) -> list[dict]:

        from admin_api import utils

        #get all the questionnaire categories from the database
        categories = QuestionCategory.objects.all()

        #list to store the category evaluations
        evals_category_list = []

        for category in categories: 

            #filter out the questionnaires under the category at the current iteration
            cat_questions = Questionnaire.objects.filter(category=category)

            category_question_evaluations: list[Evaluation] = []

            #iterate through the filterd questions
            for question in cat_questions:
                #get the evaluation answers for the question at the current iteration
                evaluations = Evaluation.objects.filter(question=question, class_course=self)
                
                if len(evaluations) == 0:
                    continue
            
                category_question_evaluations.extend(list(evaluations))

            
            total_evaluations = len(category_question_evaluations)

            #extract the answers from the list of evaluations and sum them up
            eval_answers_total_score = sum([utils.ANSWER_SCORE_DICT[evaluation.answer.lower()] for evaluation in category_question_evaluations])
            
            #find the average score of the evaluations ath current category
            cat_average_score = (eval_answers_total_score / total_evaluations) if total_evaluations != 0 else 0

            #todo: calculate the percentage score
            max_answers_score = total_evaluations * 5 #first finding the maximum score
            percentage_score = (eval_answers_total_score / max_answers_score) * 100 #value here is in percentages
            
            #append to the overall list.
            evals_category_list.append({
                'category': category.cat_name,
                'percentage_score': percentage_score,
                'average_score': cat_average_score,
                'remark': utils.categoryScoreBasedRemark(cat_average_score)
            })
                

        return evals_category_list
    



    def __repr__(self):
        return self.id, self.course.course_code, self.lecturer.user.username
    
    def __str__(self):
        return str(self.__repr__())


    def toMap(self) -> dict:

        from .core_utils import getScoreRemark

        grand_mean_score = self.computeGrandMeanScore()
        remark = getScoreRemark(grand_mean_score)

        return {
            'cc_id': self.id,
            'credit_hours': self.credit_hours,
            'has_online': self.has_online,
            'course': self.course.toMap(),
            'lecturer': self.lecturer.toMap(),
            'semester': self.semester,
            'year': self.year,
            'grand_mean_score': self.computeGrandMeanScore(),
            'lecturer_course_rating': self.computeLecturerRatingForCourse(),
            'remark': remark
        }
    
    pass






#A student registered class......Corresponding to a ClassCourse
class StudentClass(models.Model):
    id = models.AutoField(primary_key=True)
    student: Student = models.ForeignKey(Student, related_name='student', on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='class_course', on_delete=models.CASCADE)
    evaluated = models.BooleanField(default=False)

    def __str__(self):
        return f'Student Class({self.id}, {self.student.reference_number}, {self.class_course.id})'
    

    @staticmethod 
    def countEvaluatedCoursesFor(year:int, semester: int) -> int:
        class_courses = ClassCourse.objects.filter(year=year, semester=semester)

        counter = 0

        for class_course in class_courses:
            student_classes = StudentClass.objects.filter(class_course=class_course, evaluated=True)
            counter += student_classes.count()

            pass

        return counter 


        
    
    def toMap(self) -> dict:

        course: Course = self.class_course.course
        lecturer: Lecturer = self.class_course.lecturer

        return {
            'cc_id': self.class_course.id,
            'course_code': course.course_code,
            'course_title': course.title,
            'credit_hours': self.class_course.credit_hours, 
            'lecturer': lecturer.getFullName(),
            'department': lecturer.department.department_name,
            'evaluated': self.evaluated,
        }

    pass







#the category for the questions.
class QuestionCategory(models.Model):
    
    cat_id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=150, default='')

    def __repr__(self):
        return self.cat_id, self.cat_name
    
    def __str__(self):
        return str(self.__repr__())
    

    def toMap(self):
        return {
            'category_id': self.cat_id,
            'category_name': self.cat_name 
        }
    

    def getQuestions(self):
        return Questionnaire.objects.filter(category=self)
    

    pass





#the questions class
class Questionnaire(models.Model):

    q_id = models.AutoField(primary_key=True)
    category: QuestionCategory = models.ForeignKey(QuestionCategory, related_name='question_category', on_delete=models.CASCADE)
    question = models.TextField(default='')
    answer_type = models.CharField(max_length=20, default='yes_no') #"yes_no", "performance", "time"


    def __repr__(self):
        return self.category.cat_name, self.question, self.answer_type

    def __str__(self):
        return str(self.__repr__())
    
    def toMap(self):
        return {
            'id': self.q_id,
            'category': self.category.toMap(),
            'question': self.question,
            'answer_type': self.answer_type
        }
    
    pass
    



#the actual answering of the questionnaires by the students
class Evaluation(models.Model):
    answer_id = models.AutoField(primary_key=True)
    student: Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='eval_class_course', on_delete=models.CASCADE)
    question: Questionnaire = models.ForeignKey(Questionnaire, related_name='eval_questionnaire', on_delete=models.CASCADE)
    answer = models.TextField(default='')


    def __repr__(self):
        return self.answer_id, self.student.reference_number, self.answer

    def __str__(self):
        return str(self.__repr__())




class EvaluationSuggestion(models.Model):

    id = models.AutoField(primary_key=True)
    student: Student = models.ForeignKey(Student, related_name='s_student', on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='s_class_course', on_delete=models.CASCADE)
    suggestion = models.TextField(default='')



    @staticmethod  
    def countClassCoursesFor(year:int, semester:int):
        class_courses = ClassCourse.objects.filter(year=year, semester=semester)

        if len(class_courses) == 0: 
            return 0
        
        cc_count = 0

        for class_course in class_courses:
            cc_count += EvaluationSuggestion.objects.filter(class_course=class_course).count()

        return cc_count
    
    


    def __repr__(self):
        return (self.id, self.student.id, self.class_course.course.course_code, self.suggestion)
    
    def __str__(self):
        return str(self.__repr__())
    
    def toMap(self):
        return {
            'suggestion_id': self.id, 
            'suggestion': self.suggestion
        }
    pass




#the part where students rate a lecturer for a particular class_course
class LecturerRating(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, related_name='lr_student', on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='lr_cc', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'Lecturer Rating({self.id}, {self.class_course.lecturer.name}, RATING: {self.rating}, (course: {self.class_course.course.course_code}))'




#handle if a student had completed an evaluation for a particular class_course.
class EvaluationStatus(models.Model):

    id = models.AutoField(primary_key=models.CASCADE)
    student: Student = models.ForeignKey(Student, related_name='es_student', on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='es_class_course', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)



    @staticmethod
    def countClassCoursesFor(year: int, semester: int) -> int:
        class_courses = ClassCourse.objects.filter(year=year, semester=semester)


        if len(class_courses) == 0:
            return 0

        number_of_evaluations = 0

        for class_course in class_courses:
            eval_status = EvaluationStatus.objects.filter(class_course=class_course)
            number_of_evaluations += len(eval_status)
            pass
        
        return number_of_evaluations



    def __repr__(self):
        return self.id, self.student.reference_number, self.class_course.course.course_code, self.status
    
    def __str__(self):
        return str(self.__repr__())
    
    pass




