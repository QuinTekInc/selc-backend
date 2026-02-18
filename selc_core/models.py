from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.utils import timezone
from collections import Counter


# Create your models here.


class Notification(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user: User = models.OneToOneField(User, null=False, on_delete=models.CASCADE)  #whom the notification is meant for.
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

    academic_year = models.IntegerField(default=timezone.now().year)

    semester_end_date = models.DateField(default=timezone.now().date())

    enable_evaluations = models.BooleanField(default=False)


    def __repr__(self):
        return f'semester: {self.current_semester}', f'accept_evaluations: {self.enable_evaluations}'

    def __str__(self):
        return str(self.__repr__())

    def toMap(self) -> dict:
        return {
            'current_semester': self.current_semester,
            'academic_year': self.academic_year,
            'enable_evaluations': self.enable_evaluations,
            'semester_end_date': self.semester_end_date
        }


#this model will be removed and stored as plain string
class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    department_name = models.CharField(max_length=120, unique=True, null=False)

    def __repr__(self):
        return self.id, self.department_name

    def __str__(self):
        return str(self.__repr__())


    def getSavableReportFileName(self) -> str:
        return f'dept_{self.department_name}_report'

    # returns all the classcourses handled the lecturers in the department
    def getClassCourses(self, as_map=False, is_current=False) -> object:
        lecturers = Lecturer.objects.filter(department=self)

        if not is_current:
            #get the classes based on the lecturers in the department
            class_courses = ClassCourse.objects.filter(lecturer__in=lecturers)
        else: 
            class_courses = ClassCourse.getCurrentClassCourses().filter(lecturer__in=lecturers)


        if not as_map:
            return class_courses

        return [class_course.toMap() for class_course in class_courses]

    def toMap(self):
        return {
            'department_id': self.id,
            'department_name': self.department_name,
            'number_of_students': self.students.filter(is_active=True).count(), #because of the related_name param to the Department foreign key in Student model.
            'number_of_lecturers': self.lecturers.count() #because of the related_name para to the Department foreign key in Lecturer model
        }

    pass


#the student's information
class Student(models.Model):

    #the user attribute will be removed from the model as authentication will now be carried on the school's platform
    #the reference number will now become primary-key for the student model
    #the index number will be removed from the students model. 
    #store the student's full name, and program of study
    #the level attribute will be removed from this model.
    #store the attribute which checks whether is currently active or not. (is_active is false when student program shows are DEFERRED, ABANDONED, COMPLETED THEIR STUDIES)


    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE) #the reference number will become the primary-key attribute for the student model
    reference_number = models.CharField(max_length=50, null=False, unique=True) #this will become the primary key
    index_number = models.CharField(max_length=50, default='')
    department: Department = models.ForeignKey(Department, related_name='students', null=True,
                                               on_delete=models.SET_NULL) #department attribute will be replaced with just a string
    program = models.CharField(max_length=100, null=False, default='')
    campus = models.CharField(max_length=100, default='Sunyani')
    status = models.CharField(max_length=100, default='Regular')

    is_active = models.BooleanField(default=True)

    #will have to add level

    def __repr__(self):
        return self.user.username, f'REF: {self.reference_number}', self.age, self.program

    def __str__(self):
        return str(self.__repr__())

    def getRegisteredCourses(self) -> list:
        """
        This function returns a list of all the registered courses for a student 
        at the current instance studied in this current semester and academic year.
        """

        class_courses = ClassCourse.getCurrentClassCourses()

        student_classes = StudentClass.objects.filter(student=self, class_course__in=class_courses)

        return student_classes

    def getFullName(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def toMap(self, is_student_login=False):

        student_map = {
            'full_name': self.getFullName(),
            'index_number': self.index_number,
            'reference_number': self.reference_number,
            'department': self.department.department_name,
            'program': self.program,
            'age': self.age,
            'campus': self.campus,
            'status': self.status,
        }

        if is_student_login:
            token, _ = Token.objects.get_or_create(user=self.user)
            student_map['token'] = token.key

        return student_map

    pass


#the lecturers information


class Lecturer(models.Model):

    #A reference to the user model will have to be removed for the lecturer model.
    #the primary-key field will be UUID the corresponds the lecturer's id in the "organisation" database.
    #store their full names and email address
    #store the lecturer's department as a plain string

    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    department: Department = models.ForeignKey(Department, related_name='lecturers', null=True,
                                               on_delete=models.SET_NULL)

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

    def getOverallRatingSummary(self) -> list[dict]:
        #get everycourse the lecturer has taught
        class_courses = ClassCourse.objects.filter(lecturer=self)

        lecturer_ratings = []

        ratings_map_list = []

        for class_course in class_courses:
            #get the lecturer ratings for each course
            ratings = LecturerRating.objects.filter(class_course=class_course)
            lecturer_ratings.extend(ratings)
            pass

        for i in range(5, 0, -1):
            i_filtered_ratings = filter(lambda r: r.rating == i, lecturer_ratings)
            i_rating_count = len(list(i_filtered_ratings))
            i_rating_percentage = 0

            if i_rating_count > 0:
                i_rating_percentage = (i_rating_count / len(lecturer_ratings)) * 100

            rating_map = {
                'rating': i,
                'rating_count': i_rating_count,
                'percentage': i_rating_percentage
            }

            ratings_map_list.append(rating_map)

        return ratings_map_list

    #use this data to build a "trend line chart" in the frontend
    def getYearlyAverageRatingSummary(self):
        #get all the class_courses of the lecturer
        class_courses = ClassCourse.objects.filter(lecturer=self)

        years = set([class_course.year for class_course in class_courses])

        yearly_rating_dict_list: list[str, float] = []

        for year in years:
            year_class_courses = class_courses.filter(year=year)
            #get the lecturer ratings based on year_class_courses
            lecturer_ratings = LecturerRating.objects.filter(class_course__in=year_class_courses)
            total_rating = sum([l_rating.rating for l_rating in lecturer_ratings])

            average_rating = 0

            if lecturer_ratings.exists():
                average_rating = total_rating / lecturer_ratings.count()

            yearly_rating_dict_list.append({'year': year, 'average_rating': average_rating})

        return yearly_rating_dict_list

    def computeLecturerOverallAverageRating(self) -> float:

        class_courses = ClassCourse.objects.filter(lecturer=self)

        if not class_courses.exists():
            return 0

        total_ratings = 0

        for class_course in class_courses:
            lecturer_ratings = LecturerRating.objects.filter(class_course=class_course)
            total_ratings += sum([l_rating.rating for l_rating in lecturer_ratings])

        return total_ratings / len(class_courses)

    def toMap(self):

        from .core_utils import getScoreRemark

        rating = self.computeLecturerOverallAverageRating()
        remark = getScoreRemark(rating)

        return {
            'username': self.user.username,
            'name': self.getFullName(),
            'email': self.user.email.strip() if self.user.email else 'N/A',
            'rating': rating,
            'remark': remark,
            'department': self.getDepartmentName(),
        }

    pass


#this model will be removed
#course information
class Course(models.Model):
    course_code = models.CharField(primary_key=True, max_length=20, unique=True)
    title = models.CharField(max_length=200, default='')

    def __repr__(self):
        return self.course_code, self.title

    def __str__(self):
        return str(self.__repr__())


    def computeMeanScore(self, class_courses=None) -> tuple[float, float]:

        if class_courses is None or len(class_courses) == 0: 
            return 0, 0

        score_tuples = [cc.computeGrandMeanScore() for cc in class_courses]

        mean_scores = [score_tuple[0] for score_tuple in score_tuples]

        total_mean_score = sum(mean_scores)

        course_mean_score: float = total_mean_score / len(mean_scores) if len(mean_scores) != 0 else 0

        course_percentage: float = (course_mean_score/ 5) * 100

        return course_mean_score, course_percentage


    #info: this method calculates the cummulative performance rating and remarks of the course.
    #this calculation is based on the class_courses related to the current course.
    def computeOverallCourseMeanScore(self) -> tuple[float, float]:
        #get all the class courses corresponding to this class.
        class_courses = ClassCourse.objects.filter(course=self)
        return self.computeMeanScore(class_courses)


    def computeCurrentSemesterMeanScore(self):
        class_courses = ClassCourse.getCurrentClassCourses().filter(course=self)
        return self.computeMeanScore(class_courses)



    def courseInfo(self):

        from .core_utils import getScoreRemark

        general_setting = GeneralSetting.objects.first()

        #lecturers who have handled this course (as class_course)
        class_courses = ClassCourse.objects.filter(course=self)

        #total number of classes
        total_classes = class_courses.count()

        #overall_mean_score and percentage score
        overall_mean_score, overall_percentage = self.computeMeanScore(class_courses)
        
        #overall remark for this [based on overall_average_scores of the classes for this course]
        overall_remark = getScoreRemark(overall_mean_score)

        current_class_courses = class_courses.filter(semester=general_setting.current_semester, year=general_setting.academic_year)

        #lecturers currently handling this course
        number_of_lecturers = current_class_courses.count()

        #mean_score and percentage score for the semester
        mean_score, percentage_score = self.computeMeanScore(current_class_courses)
        
        #remark of course performance for the semester
        current_remark = getScoreRemark(mean_score)

        #the total number of students currently learning this course
        students_counts: list[tuple] = [class_course.getNumberOfRegisteredStudents() for class_course in current_class_courses]

        registered_students_count = sum([student_count[0] for student_count in students_counts])
        evaluated_students_count = sum([student_count[1] for student_count in students_counts])

        response_rate = (evaluated_students_count / registered_students_count) * 100 if registered_students_count != 0  else 0

        course_info_map = {
            'total_classes': total_classes,
            'overall_mean_score': float(overall_mean_score), 
            'overall_percentage_score': overall_percentage,
            'overall_remark': overall_remark,
            'c_number_of_lecturers': number_of_lecturers,
            'c_mean_score': mean_score, 
            'c_percentage_score': percentage_score,
            'remark': current_remark, 
            'registered_students': registered_students_count, 
            'evaluated_students': evaluated_students_count,
            'response_rate': response_rate,
            'cummulative_class_courses': [class_course.toMap() for class_course in class_courses],
            'current_class_courses': [class_course.toMap() for class_course in current_class_courses],
        }


        return course_info_map

    def toMap(self):
        from .core_utils import getScoreRemark

        mean_score, percentage = self.computeOverallCourseMeanScore()
        remark = getScoreRemark(mean_score)

        c_mean_score, c_percentage = self.computeCurrentSemesterMeanScore()
        c_remark = getScoreRemark(c_mean_score)


        return {
            'course_code': self.course_code,
            'course_title': self.title,
            
            'mean_score': mean_score,
            'percentage_score': percentage,
            'remark': remark,

            'c_mean_score': c_mean_score,
            'c_percentage_score': c_percentage,
            'c_remark': c_remark
        }

    pass


class SessionChoices(models.TextChoices):
    MAINSTREAM = ('MAINSTREAM', 'mainstream')
    WEEKEND = ('WEEKEND', 'weekend')




#assigns courses to lecturers for a particular semester and academic year
class ClassCourse(models.Model):

    #the id or primary-key attribute will be a uuid field.
    #course_code and course title will be stored as plain string
    #store the level for the class course or mounted course.
    #the academic_year attribute will be stored as a string instead of integer.
    #store the semester as an integer.
    #the lecturer attribute will be foreign key reference to the lecturer model.
    #a variable to check if responses are beign taken for the current course.

    id = models.AutoField(primary_key=True)
    course: Course = models.ForeignKey(Course, related_name='class_courses', on_delete=models.CASCADE)
    credit_hours = models.IntegerField(default=3)
    lecturer: Lecturer = models.ForeignKey(Lecturer, related_name='class_courses', on_delete=models.CASCADE)
    class_session = models.CharField(max_length=20, default='mainstream', choices=SessionChoices.choices)
    level = models.CharField(max_length=4, default='')
    semester = models.IntegerField(default=1)
    year = models.IntegerField(null=True)
    has_online = models.BooleanField(default=False)
    is_accepting_response = models.BooleanField(default=True)

    def getSavableReportFileName(self):
        return f'{self.year}0{self.semester}_{self.course.course_code}_{self.lecturer.getFullName()}'

    #this methods lists all the ClassCourses offered in an academic year
    @staticmethod
    def getCurrentClassCourses():

        general_setting = GeneralSetting.objects.all().first()

        class_courses = ClassCourse.objects.filter(semester=general_setting.current_semester,
                                                   year=general_setting.academic_year)

        return class_courses

    #returns the average lecturer rating got this course
    def computeLecturerRatingForCourse(self, ratings=None):

        if ratings is None:
            ratings = LecturerRating.objects.filter(class_course=self)

        if ratings.count() == 0:
            return 0

        ratings_sum = sum([rating.rating for rating in ratings])
        average_rating = ratings_sum / len(ratings)

        return average_rating
        

    #the mean score for the course.
    def computeGrandMeanScore(self, evaluations=None) -> tuple:

        from .core_utils import ANSWER_SCORE_DICT

        if evaluations is None:
            #get all the course evaluations
            evaluations = Evaluation.objects.filter(class_course=self)

        total_evaluations = evaluations.count()

        if total_evaluations == 0:
            return 0, 0

        ##filter the questionnaire answers where the answer_type to the question is "performance"

        # performance_evaluations = list(filter(
        #     lambda evaluation: evaluation.question.answer_type == 'performance', evaluations))

        #get the answers for to each questionnaire for this class_course, convert the answer to a value in the scale of 1-5,
        #collect them a list and find the total sum of all the values.
        total_performance_score = sum(
            [ANSWER_SCORE_DICT.get(evaluation.answer.lower(), 0) for evaluation in evaluations])

        #compute the average score.
        grand_mean_score = total_performance_score / total_evaluations

        grand_percentage_score = (grand_mean_score / 5) * 100

        return grand_mean_score, grand_percentage_score


    #returns the list program_classes(students program) to which this class course is taught
    def getListOfProgramsInClass(self) -> list:
        unique_programs = list(
            StudentClass.objects.filter(class_course=self,)
            .values_list('student__program', flat=True)
            .distinct()
        )
        return unique_programs


    #method fo compute the number of students who have registered for the course
    def getNumberOfRegisteredStudents(self, students_classes=None) -> tuple[int, int]:

        if students_classes is None:
            students_classes = StudentClass.objects.filter(class_course=self)

        if not students_classes.exists():
            return (0, 0)

        registered_students = students_classes.count()

        evaluated_count = students_classes.filter(evaluated=True).count()

        return (registered_students, evaluated_count)


    #todo: rename this method to "getLecturerRating"
    def getLecturerRatingDetails(self) -> list[dict]:

        this_class_course_ratings = LecturerRating.objects.filter(class_course=self)

        ratings_map_list: list[dict] = []

        for i in range(5, 0, -1):

            i_ratings = filter(lambda lr: lr.rating == i, this_class_course_ratings)

            rating_count = len(list(i_ratings))

            percentage = 0

            if rating_count > 0:
                percentage = (rating_count / len(this_class_course_ratings)) * 100

            ratings_map = {
                'rating': i,
                'rating_count': rating_count,
                'percentage': percentage
            }

            ratings_map_list.append(ratings_map)

            pass

        return ratings_map_list


    #returns the suggestions and sentiments tone of the suggestion
    def getEvalSuggestions(self, include_suggestions=True, suggestions=None) -> dict:

        if suggestions is None:
            suggestions = EvaluationSuggestion.objects.filter(class_course=self)

        sentiments = [suggestion.sentiment for suggestion in suggestions]

        sentiment_summary_list = []

        for sentiment in ('negative', 'neutral', 'positive'):
            filtered_sentiments = filter(lambda s: s.lower() == sentiment, sentiments)
            sentiment_count = len(list(filtered_sentiments))

            sentiment_percent = 0

            if sentiment_count != 0:
                sentiment_percent = (sentiment_count / len(sentiments)) * 100

            sentiment_map = {
                'sentiment': sentiment,
                'sentiment_count': sentiment_count,
                'sentiment_percent': sentiment_percent
            }

            sentiment_summary_list.append(sentiment_map)

        suggestions_map = [suggestion.toMap(include_lecturer_rating=True, include_program=True) for suggestion in suggestions]

        if not include_suggestions:
            return {'sentiment_summary': sentiment_summary_list}
        else:
            return {
                'sentiment_summary': sentiment_summary_list,
                'suggestions': suggestions_map
            }


    def getQuestionAnswerSummary(self, question, evaluations) -> dict:

        from . import core_utils as utils

        question_answers = evaluations.values_list('answer', flat=True)

        answer_summary = dict(Counter(question_answers))

        #some possible answers may not be found so we add them manually to the dictionary
        #and set their counts to zero
        possible_answers = utils.ANSWER_TYPE_DICT.get(question.answer_type.lower(), [])

        for possible_answer in possible_answers:
            if possible_answer in answer_summary:
                continue

            answer_summary[possible_answer] = 0
            pass


        question_eval_dict = {
            'question': question.question,
            'answer_type': question.answer_type,
            'answer_summary': answer_summary,
        }

        total_evaluations = evaluations.count()
        total_answer_score = 0

        for possible_answer, count in answer_summary.items():
            answer_score = utils.ANSWER_SCORE_DICT.get(possible_answer.lower(), 0)
            total_answer_score += answer_score * count
            pass

        # calculate the average answer score.
        percentage_score = 0
        mean_answer_score = 0

        # if max_answer_score > 0:
        if total_evaluations > 0:
            mean_answer_score = total_answer_score / total_evaluations
            # percentage_score = (total_answer_score / max_answer_score) * 100
            percentage_score = (mean_answer_score / 5) * 100  # since the maximum score you can get for a questionnaire item is 5

        # update the dictionary
        question_eval_dict['mean_score'] = mean_answer_score
        question_eval_dict['percentage_score'] = percentage_score
        question_eval_dict['remark'] = utils.getScoreRemark(mean_answer_score)

        return question_eval_dict


    #todo: rename this to "getQuestionnaireAnswerSummary"
    def getEvalDetails(self, evaluations=None) -> list[dict]:

        #data is returned the format below
        """
        [

            {
                "category": "Course Content",
                "mean_score": 4.75,
                "percentage_score": 95.0,
                "remark": "Excellent",
                "questions": [
                    {
                        "question": "Lecturer has provided helpful course outline",
                        "answer_type": "performance",
                        "answer_summary": {
                            "Excellent": 1
                        },
                        "percentage_score": 100.0,
                        "average_score": 5.0,
                        "remark": "Excellent"
                    },

                ]
            },

        ]
        """

        from . import core_utils as utils

        #get the evaluations 
        if evaluations is None: 
            evaluations = Evaluation.objects.filter(class_course=self)

        #get the categories
        categories = QuestionCategory.objects.all()

        cat_list = []


        for category in categories:

            cat_map = {
                'category': category.cat_name
            }

            #get the questions
            questionnaires = Questionnaire.objects.filter(category=category)

            #get the answers to the list of questions under the category
            #the goal is to calculate the mean and percentage scores of the category

            evaluation_answers = evaluations.filter(question__in=questionnaires).values_list('answer', flat=True)

            total_answer_score = sum([utils.ANSWER_SCORE_DICT.get(answer.lower(), 0) for answer in evaluation_answers])

            cat_mean_score = 0
            cat_percentage_score = 0

            if len(evaluation_answers) > 0:
                cat_mean_score = total_answer_score / len(evaluation_answers)
                cat_percentage_score = (cat_mean_score / 5) * 100


            cat_map['mean_score'] = cat_mean_score
            cat_map['percentage_score'] = cat_percentage_score
            cat_map['remark'] = utils.getScoreRemark(cat_mean_score)


            questions_list = []

            for questionnaire in questionnaires:
                question_evaluations = evaluations.filter(question=questionnaire)
                question_answer_summary = self.getQuestionAnswerSummary(questionnaire, question_evaluations)
                questions_list.append(question_answer_summary)
                pass

            cat_map['questions'] = questions_list

            cat_list.append(cat_map)


        return cat_list



    def getEvalDetailsByProgram(self, program):

        program_students = (Student.objects
                            .filter(registrations__class_course=self, program=program).distinct())

        evaluations = Evaluation.objects.filter(class_course=self, student__in=program_students)

        return self.getEvalDetails(evaluations)



    def getEvalSuggestionByProgram(self, program, include_suggestions=True,):
        program_students = (Student.objects
                            .filter(registrations__class_course=self, program=program)
                            .distinct())

        suggestions = EvaluationSuggestion.objects.filter(class_course=self, student__in=program_students)

        return self.getEvalSuggestions(include_suggestions, suggestions)



    def getCCDetailByProgram(self):
        programs = self.getListOfProgramsInClass()

        cc_program_info_maps: list[dict] = []

        from .core_utils import getScoreRemark

        for program in programs:

            program_students = (Student.objects
                                .filter(registrations__class_course=self, program=program))

            program_evaluations: list[Evaluation] = self.evaluations.filter(student__in=program_students)

            program_student_classes = self.registrations.filter(student__in=program_students)

            program_lecturer_ratings = LecturerRating.objects.filter(class_course=self, student__in=program_students)

            # program_suggestions: list[EvaluationSuggestion] = self.evaluation_suggestions.fillter(student__int=program_students)



            p_mean_score, p_percentage_score = self.computeGrandMeanScore(evaluations=program_evaluations)

            p_remark = getScoreRemark(p_mean_score)


            p_registered_students, p_evaluated_students = self.getNumberOfRegisteredStudents(program_student_classes)

            p_response_rate = (p_evaluated_students / p_registered_students) * 100 if p_registered_students != 0 else 0


            program_average_lecturer_rating = self.computeLecturerRatingForCourse(ratings=program_lecturer_ratings)

            cc_program_info_maps.append({
                'program': program,
                'number_of_registered_students': p_registered_students,
                'number_of_evaluated_students': p_evaluated_students,
                'response_rate': p_response_rate,

                'mean_score': p_mean_score,
                'percentage_score': p_percentage_score,
                'remark': p_remark,

                'lecturer_rating': program_average_lecturer_rating
            })


        return cc_program_info_maps



    def getProgramPopulation(self, program):
        students_classes = self.registrations.filter(student__program=program)
        return self.getNumberOfRegisteredStudents(students_classes)


    #todo: remake this method to "getQuestionnaireCategoriesSummary"
    def getEvalQuestionCategoryRemarks(self, include_questions=False) -> list[dict]:

        from . import core_utils as utils

        evaluations = Evaluation.objects.filter(class_course=self)

        #get all the questionnaire categories from the database
        categories = QuestionCategory.objects.all()

        #list to store the category evaluations
        evals_category_list = []

        for category in categories:

            #filter out the questionnaires under the category at the current iteration
            cat_questions = Questionnaire.objects.filter(category=category)

            category_question_evaluations: list[Evaluation] = []

            #iterate through the filtered questions
            for question in cat_questions:
                #get the evaluation answers for the question at the current iteration
                question_evaluations = evaluations.filter(question=question)

                if len(evaluations) == 0:
                    continue

                category_question_evaluations.extend(list(evaluations))
                pass

            total_evaluations = len(category_question_evaluations)


            for evaluation in category_question_evaluations:
                if evaluation.answer.lower() == 'often':
                    print(evaluation.answer_id)
                    print(evaluation.answer)
                    print(evaluation.question.question)


            #extract the answers from the list of evaluations and sum them up
            eval_answers_total_score = sum(
                [utils.ANSWER_SCORE_DICT[evaluation.answer.lower()] for evaluation in category_question_evaluations])

            #find the average score of the evaluations ath current category
            cat_average_score = (eval_answers_total_score / total_evaluations) if total_evaluations != 0 else 0

            #max_answers_score = 0
            percentage_score = 0

            #todo: calculate the percentage score
            if total_evaluations > 0:
                #max_answers_score = total_evaluations * 5 #first finding the maximum score
                #percentage_score = (eval_answers_total_score / max_answers_score) * 100 #value here is in percentages
                percentage_score = (cat_average_score / 5) * 100

            category_map = {
                'category': category.cat_name,
                'percentage_score': percentage_score,
                'average_score': cat_average_score,
                'remark': utils.getScoreRemark(cat_average_score)
            }

            if include_questions:
                category_map['questions'] = [question.toMap() for question in cat_questions]

            #append to the overall list.
            evals_category_list.append(category_map)

        return evals_category_list

    def __repr__(self):
        return self.id, self.course.course_code, self.lecturer.user.username

    def __str__(self):
        return str(self.__repr__())

    def toMap(self) -> dict:

        from .core_utils import getScoreRemark

        grand_mean_score, grand_percentage = self.computeGrandMeanScore()

        remark = getScoreRemark(grand_mean_score)

        programs = self.getListOfProgramsInClass()
        registered_students_count, evaluated_students_count = self.getNumberOfRegisteredStudents()

        response_rate = (evaluated_students_count / registered_students_count) * 100

        return {
            'cc_id': self.id,
            'credit_hours': self.credit_hours,
            'has_online': self.has_online,
            'course': self.course.toMap(),
            'lecturer': self.lecturer.toMap(),
            'level': self.level,
            'semester': self.semester,
            'year': self.year,
            'is_accepting_response': self.is_accepting_response,
            'grand_mean_score': grand_mean_score,
            'grand_percentage': grand_percentage,
            'lecturer_course_rating': self.computeLecturerRatingForCourse(),
            'number_of_registered_students': registered_students_count,
            'number_of_evaluated_students': evaluated_students_count,
            'response_rate': response_rate,
            'remark': remark,
            'programs': programs
        }

    pass


#A student registered class......Corresponding to a ClassCourse
#todo: rename this model or class to "RegisteredClass"
class StudentClass(models.Model):
    id = models.AutoField(primary_key=True)
    student: Student = models.ForeignKey(Student, related_name='registrations', on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='registrations', on_delete=models.CASCADE)
    evaluated = models.BooleanField(default=False)

    def __str__(self):
        return f'Student Class({self.id}, {self.student.reference_number}, {self.class_course.id})'

    @staticmethod
    def countEvaluatedCoursesFor(year: int, semester: int) -> int:
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
            'is_accepting_response': self.class_course.is_accepting_response,
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
    category: QuestionCategory = models.ForeignKey(QuestionCategory, related_name='questionnaires', null=True,
                                                   on_delete=models.SET_NULL)
    question = models.TextField(default='')
    answer_type = models.CharField(max_length=20, default='yes_no')  #"yes_no", "performance", "time"

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
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='evaluations',
                                                  on_delete=models.CASCADE)
    question: Questionnaire = models.ForeignKey(Questionnaire, related_name='evaluations',
                                                on_delete=models.CASCADE)
    answer = models.TextField(default='')

    def __repr__(self):
        return self.answer_id, self.student.reference_number, self.answer

    def __str__(self):
        return str(self.__repr__())


class SentimentChoices(models.TextChoices):
    POSITIVE = ('POSITIVE', 'positive')
    NEUTRAL = ('NEUTRAL', 'netural')
    NEGATIVE = ('NEGATIVE', 'negative')


class EvaluationSuggestion(models.Model):
    id = models.AutoField(primary_key=True)
    student: Student = models.ForeignKey(Student, related_name='evaluation_suggestions', on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='evaluation_suggestions', on_delete=models.CASCADE)
    suggestion = models.TextField(default='')
    sentiment = models.CharField(max_length=20, default='neutral', choices=SentimentChoices.choices)

    #this method returns the total number of all evaluations suggestions made in 
    #specified semester in a specified academic year
    #todo: rename this method to  "countAllSuggestionsFor"
    @staticmethod
    def countClassCoursesFor(year: int, semester: int):

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

    def toMap(self, include_lecturer_rating=False, include_program=False):

        suggestion_map = {
            'suggestion_id': self.id,
            'suggestion': self.suggestion,
            'sentiment': self.sentiment
        }

        if include_lecturer_rating:
            lecturer_rating = LecturerRating.objects.get(class_course=self.class_course, student=self.student)
            suggestion_map['rating'] = lecturer_rating.rating
            pass


        if include_program:
            student_program = self.student.program 
            suggestion_map['program'] = student_program
            pass

        return suggestion_map

    pass




#the part where students rate a lecturer for a particular class_course
class LecturerRating(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, related_name='lecturer_rating', on_delete=models.CASCADE)
    class_course: ClassCourse = models.ForeignKey(ClassCourse, related_name='lecturer_rating', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'Lecturer Rating({self.id}, {self.class_course.lecturer.name}, RATING: {self.rating}, (course: {self.class_course.course.course_code}))'




#the report file model
class ReportFile(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    file_name = models.TextField()
    file = models.FileField(upload_to='evaluation-reports/', null=True)
    file_type = models.CharField(max_length=10, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f'({self.file_name, self.file_type})'

    def __str__(self):
        return str(self.__repr__())

    def toMap(self, request = None):

        file_url = request.build_absolute_uri(self.file.url) if self.file and request else None

        return {
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_url': file_url
        }
    pass
