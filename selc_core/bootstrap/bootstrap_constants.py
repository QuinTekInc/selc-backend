

questions_and_categories = [
    #todo: section for the course content
    {
        'category': 'Course Content',
        'questions': [
            {
                'question': 'Lecturer has provided helpful course outline',
                'answer_type': 'performance',
            },

            {
                'question': 'Coverage of course content by lecturer',
                'answer_type': 'performance',
            },

            {
                'question': 'Communication of objectives of the course',
                'answer_type': 'performance',
            },

            {
                'question': 'Relevant reading materials and references provided(textbooks, links, lecturer notes, videos etc)',
                'answer_type': 'performance',
            },
        ]
    },


    #todo: section for the class attendance

    {
        'category': 'Class Attendance',
        'questions': [
            {
                'question': 'Regularity in class',
                'answer_type': 'performance',
            },

            {
                'question': 'Punctuality',
                'answer_type': 'performance',
            },

            {
                'question': 'Does the course have an online teaching period on this timetable ?',
                'answer_type': 'yes_no',
            },

            {
                'question': 'How often does the lecturer use the online teaching period ?',
                'answer_type': 'time',
            },
        ]
    }, 


    #todo: section for Mode of delivery or interactions

    {
        'category': 'Mode of Delivery / Interactions',
        'questions': [
            {
                'question': 'Lecturer explains the material clearly in ways that easy to understand, offer alternative explanations or additional examples and clears up confusion',
                'answer_type': 'performance',
            },

            {
                'question': 'Encouraging student participation during learning',
                'answer_type': 'performance',
            },

            {
                'question': 'Interaction with students in class',
                'answer_type': 'performance',
            },


            {
                'question': 'The lecturer is available to students outside class time for tutoring, review work or answer questions',
                'answer_type': 'performance',
            },

            {
                'question': 'The lecturer links learning materials to practical applications.',
                'answer_type': 'performance',
            },

        ]
    },

    #todo: section for asssessment of materials taught

    {
        'category': 'Assesssment of Materials Taught',
        'questions': [
            {
                'question': 'The lecturer is approchable; He/She demonstrates interest in and concerns for the students',
                'answer_type': 'performance',
            },

            {
                'question': 'The lecturer gives the right amounts of graded assignments, tests and quizzes, in order to fairly evaluate performance',
                'answer_type': 'performance',
            },


            {
                'question': 'Marking and discussion of class assignment.',
                'answer_type': 'performance',
            },


            {
                'question': 'Monitoring the the progress of the class (Attendance, Student performance)',
                'answer_type': 'performance',
            },
        ]
    }, 


    #todo: section for the use of teaching assistants.
    {
        'category': 'Use of Teaching Assistants',
        'questions': [
            {
                'question': 'Is this lecturer having a teaching assistant ?',
                'answer_type': 'yes_no',
            },

            {
                'question': 'How often does the teaching assistance do tutorials in the absence of the lecturer?',
                'answer_type': 'time',
            },

        ]
    },  

]





#NOTE: the permissions section stores the code names for each action that can be peformed on the database.
groups_and_permissions: list[dict] = [

    {
        'group': 'superuser', # overall permission holder
        'permissions': ['*'] #has all permissions required
    },

    {
        'group': 'admin', # helps to assess data.
        'permissions': ['view_lecturer', 'view_course', 'view_classcourse', 'view_evaluation', 'view_questionnaire', 'view_evaluationsuggestion']
    },

    {
        'group': 'lecturer', # responsible for viewing accessed data
        'permissions': ['view_lecturer', 'view_course', 'view_classcourse', 'view_evaluation', 'view_evaluationsuggestion', 'view_lecturerrating']
    },

    {
        'group': 'student', # responsible for entering data.
        'permissions': ['view_student', 'view_questionnaire', 'add_evaluation', 'add_evaluationsuggestion', 'add_lecturerrating']
    },
    
]





#dummy departments data
dummy_departments_data = [
    "Computer Science and Informatics", 
    "Information Technology and Decision Sciences", 
    "Arts and General Studies", 
    "Mathematics"
]


#list of lecturers who taught us the second semester 2025
#BSC Computer Science Level 200
dummy_lecturers_data = [

    {
        "username": "pkmensah",
        "name": 'Prof. Patrick .K Mensah',
        "email": "pkmensah@uenr.gh", 
        "department": "Computer Science and Informatics"
    },

    {
        "username": 'mighty',
        "name": "Dr. Mighty Ayidzoe",
        "email": "mightyayi@uenr.gh",
        "department": "Computer Science and Informatics"
    },

    {
        "username": 'obedappiah',
        "name": "Dr. Obed Appiah",
        "email": "obedapp@uenr.gh",
        "department": "Computer Science and Informatics"
    },

    {
        "username": 'bernardandoh',
        "name": "Master Benard Andoh",
        "email": "andohben@uenr.gh",
        "department": "Computer Science and Informatics"
    },

    {
        "username": "vaagyapong",
        "name": "Vivian Akoto Agyapong",
        "email": "vaagyapong",
        'department': 'Computer Science and Informatics'
    },

    {
        "username": "dratakyi",
        'name': 'Dr. A. Takyi',
        'email': 'datakyi@uenr.edu.gh',
        'department': 'Computer Science and Informatics'
    },

    {
        "username": "fumarbawah",
        'name': 'Faiza Umar Bawah',
        'email': 'fumarbawah@uenr.edu.gh',
        'department': 'Computer Science and Informatics'
    },

    {
        "username": 'nsawarayi',
        'name': 'Nicodemus Sengose Awarayi',
        'email': 'nsawarayi@uenr.edu.gh',
        'department': 'Computer Science and Informatics'
    },

    {
        "username": 'isaacaboagye',
        'name': 'Isaac Aboagye',
        'email': 'isaac_aboagye@uenr.edu.gh',
        'department': 'Arts and General Studies'
    },


    {
        "username": "drcozy",
        "name": "Cosmas Amernovi",
        'email': 'cozy@uenr.edu.gh',
        'department': 'Arts and General Studies'
    },

    {
        'username': 'kkmesah',
        'name': 'Kennedy K. Mensah',
        'email': 'kmensah@gmail.com',
        'department': 'Mathematics'
    },



    {
        'username': 'ktwaiah',
        'name': 'Kassim Tawiah',
        'email': 'ktwiah@gmail.com',
        'department': 'Mathematics'
    },

]






dummy_courses_data = [
    {
        "course_code": "COMP 168",
        "course_title": "Discrete Structures and Computations"
    },

    {
        "course_code": "MATH 101",
        "course_title": "Calculus 1"
    },

    {
        "course_code": "COMP 151",
        "course_title": "Principles Of Programming"
    },

    {
        "course_code": "COMP 153",
        "course_title": "Information Systems"
    },

    {
        "course_code": "INFT 151",
        "course_title": "Fundamentals of Computing"
    },

    {
        "course_code": "UENR 105",
        "course_title": "Introduction to French"
    },

    {
        "course_code": "COMP 165",
        "course_title": "Statistics for Computer Science"
    },

    {
        "course_code": "UENR 110",
        "course_title": "Ghanaian and African Studies"
    },

    {
        "course_code": "MATH 152",
        "course_title": "Calculus II"
    },

    {
        "course_code": "UENR 106",
        "course_title": "Introduction to French II"
    },

    {
        "course_code": "COMP 152",
        "course_title": "Programming with C++"
    },

    {
        "course_code": "COMP 154",
    
        "course_title": "Introduction to Computer Science"},
    {
        "course_code": "COMP 166",
        "course_title": "Discrete Structures and Computations"
    },

    {
        "course_code": "UENR 102",
        "course_title": "Acadmic Writing and Communication Skills II"
    },

    {
        "course_code": "UENR 101",
        "course_title": "Academic Writing and Communication Skills"
    },

    {
        "course_code": "INFT 152",
        "course_title": "Computer Ethics"
    },

    {
        "course_code": "COMP 251",
        "course_title": "Data Communication and Computer Networks"
    },

    {
        "course_code": "COMP 255",
        "course_title": "System Analysis and Design"
    },

    {
        "course_code": "COMP 261",
        "course_title": "Digital Electronics"
    },

    {
        "course_code": "COMP 257",
        "course_title": "Database Systems"
    },

    {
        "course_code": "COMP 253",
     "course_title": "Data Strucutres and Algorithms"
    },

    {
        "course_code": "UENR 201",
        "course_title": "Analytical Reading and Reasoning"
    },

    {
        "course_code": "UENR 203",
        "course_title": "French for general communication I"
    },

    {
        "course_code": "COMP 252",
        "course_title": "Computer Organization and Architecture"
    },

    {
        "course_code": "COMP 254",
        "course_title": "Advance Database"
    },

    {
        "course_code": "COMP 256",
        "course_title": "Object-Oriented Programming with Java"
    },

    {
        "course_code": "COMP 258",
        "course_title": "Software Engineering"
    },

    {
        "course_code": "COMP 262",
        "course_title": "Numerical Computation and Analysis"
    },

    {
        "course_code": "COMP 264",
        "course_title": "Computer Science Lab"
    },

    {
        "course_code": "UENR 202",
        "course_title": "Science, Technology and the Society"
    },

    {
        "course_code": "UENR 204",
        "course_title": "French for general communication II"
    },
]





"""
Each data is of the form: 
    {
        'course_code': course_code,
        'username': lecturer's username
    }
"""

dummy_class_courses = [
    #for the level hundreds
    {
        'course_code': 'COMP 152',
        'username': 'nsawarayi',
    }

]





dummy_students_data = [
    {
        'username': 'UENRUA2300644',
        'name': 'Quincy Hafes Quincy Sefalloyd',
        'reference_number': 'UA23300644',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2300751',
        'name': 'Ama Serwaa Boateng',
        'reference_number': 'UA23300751',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2300822',
        'name': 'Kwame Yeboah',
        'reference_number': 'UA23300822',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2300960',
        'name': 'Adjoa Nyamekye Owusu',
        'reference_number': 'UA23300960',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2301045',
        'name': 'Michael Owusu Afriyie',
        'reference_number': 'UA23301045',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2301178',
        'name': 'Patience Dela Kpodo',
        'reference_number': 'UA23301178',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2301234',
        'name': 'Kojo Antwi Mensah',
        'reference_number': 'UA23301234',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2301345',
        'name': 'Akosua Afriyie Sarpong',
        'reference_number': 'UA23301345',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2301402',
        'name': 'Yaw Owusu Agyeman',
        'reference_number': 'UA23301402',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    },
    {
        'username': 'UENRUA2301550',
        'name': 'Efua Sika Ofori',
        'reference_number': 'UA23301550',
        'department': 'Computer Science and Informatics',
        'program': 'B.sc Computer Science'
    }
]




