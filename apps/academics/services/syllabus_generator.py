from django.conf import settings

class SyllabusGenerator:
    """
    Service to generate syllabus content based on simplified logic.
    In a real-world scenario, this could connect to an AI service.
    """
    
    COMMON_SYLLABI = {
        'mathematics': {
            'topics': ["Number Systems", "Algebra (Polynomials, Linear Equations)", "Coordinate Geometry", "Geometry (Triangles, Circles)", "Trigonometry", "Mensuration", "Statistics and Probability"],
            'books': "NCERT Mathematics, R.D. Sharma",
            'pattern': {"Theory": 80, "Internal Assessment": 20}
        },
        'science': {
            'topics': ["Chemical Substances - Nature and Behaviour", "World of Living", "Natural Phenomena", "Effects of Current", "Natural Resources"],
            'books': "NCERT Science, Lakhmir Singh",
            'pattern': {"Theory": 80, "Practical": 20}
        },
        'english': {
            'topics': ["Reading Skills (Comprehension)", "Writing Skills (Letters, Essays)", "Grammar (Tenses, Modals)", "Literature (Prose and Poetry)"],
            'books': "NCERT Beehive, Moments",
            'pattern': {"Reading": 20, "Writing & Grammar": 30, "Literature": 30}
        },
        'computer': {
            'topics': ["Computer Basics", "Office Tools (Word, Excel, PowerPoint)", "Programming logic (Python/Java basics)", "Internet and Web Safety"],
            'books': "Computer Science by Sumita Arora",
            'pattern': {"Theory": 50, "Practical": 50}
        },
        'social science': {
            'topics': ["History (India and Contemporary World)", "Geography (Contemporary India)", "Political Science (Democratic Politics)", "Economics (Understanding Economic Development)"],
            'books': "NCERT Social Science Textbooks",
            'pattern': {"Theory": 80, "Project Work": 20}
        }
    }

    @staticmethod
    def generate(class_name, subject_name):
        """
        Generate syllabus details based on class and subject.
        """
        # Normalize subject name
        subject_key = subject_name.lower()
        result = {
            'topics': ["No standard syllabus found for this subject."],
            'recommended_books': "Consult class teacher.",
            'reference_materials': "-",
            'assessment_pattern': {"Standard": "Assessment Pattern"}
        }

        # Simple keyword matching
        for key, data in SyllabusGenerator.COMMON_SYLLABI.items():
            if key in subject_key:
                result['topics'] = data['topics']
                result['recommended_books'] = data['books']
                result['assessment_pattern'] = data['pattern']
                break
        
        # Customize based on class level (simple heuristic)
        if hasattr(class_name, 'numeric_name'):
             level = class_name.numeric_name
             if level and level > 10 and 'mathematics' in subject_key:
                 result['topics'] = ["Sets and Functions", "Trigonometric Functions", "Calculus (Limits and Derivatives)", "Coordinate Geometry (Conic Sections)", "Statistics and Probability"]
             elif level and level > 10 and 'physics' in subject_key:
                 result['topics'] = ["Physical World and Measurement", "Kinematics", "Laws of Motion", "Work, Energy and Power", "Thermodynamics", "Gravitation"]
                 result['recommended_books'] = "H.C. Verma, NCERT Physics"

        return result
