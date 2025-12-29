from apps.students.models import Student
from apps.academics.models import TimeTable, AcademicYear, SchoolClass, Section

def run():
    print("--- Debugging Portal Timetable Data ---")
    
    # Get the first student user (assuming user logged in as the first available student or similar)
    # Ideally we'd know the specific username, but let's grab the first one for now as likely only one exists in dev
    student = Student.objects.first()
    
    if not student:
        print("ERROR: No student profile found!")
        return

    print(f"Student: {student.first_name} {student.last_name} ({student.admission_number})")
    print(f"  Current Class: {student.current_class} (ID: {student.current_class_id})")
    print(f"  Section: {student.section} (ID: {student.section_id})")
    print(f"  Academic Year: {student.academic_year} (ID: {student.academic_year_id})")
    
    if not student.current_class:
        print("  WARNING: Student has no Current Class assigned!")
    
    if not student.academic_year:
        print("  WARNING: Student has no Academic Year assigned!")

    print("\n--- Checking TimeTable Entries ---")
    
    # 1. Check for ANY entries for this class
    entries_class = TimeTable.objects.filter(class_name=student.current_class).count()
    print(f"Entries for Class '{student.current_class}': {entries_class}")
    
    # 2. Check for entries for Class + Section
    entries_section = TimeTable.objects.filter(
        class_name=student.current_class,
        section=student.section
    ).count()
    print(f"Entries for Class '{student.current_class}' + Section '{student.section}': {entries_section}")
    
    # 3. Check for entries for Class + Section + Year
    entries_full = TimeTable.objects.filter(
        class_name=student.current_class, 
        section=student.section,
        academic_year=student.academic_year
    ).count()
    print(f"Entries for Class + Section + Year '{student.academic_year}': {entries_full}")
    
    if entries_full == 0 and entries_class > 0:
        print("\n--- Diagnosis ---")
        print("Entries exist for the class, but mismatch on Section or Year.")
        
        # Check Year mismatch
        years = TimeTable.objects.filter(class_name=student.current_class).values_list('academic_year__name', flat=True).distinct()
        print(f"Timetable entries found for years: {list(years)}")
        
        # Check Section mismatch
        sections = TimeTable.objects.filter(class_name=student.current_class).values_list('section__name', flat=True).distinct()
        print(f"Timetable entries found for sections: {list(sections)}")
