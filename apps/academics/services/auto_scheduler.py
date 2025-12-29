from ortools.sat.python import cp_model
from django.db import transaction
from django.core.exceptions import ValidationError
from collections import defaultdict
import logging

from apps.academics.models import (
    TimeTable, SchoolClass, Section, ClassSubject,
    AcademicYear, Subject, Holiday
)

logger = logging.getLogger(__name__)

class AutoTimetableGenerator:
    """
    Automatic Timetable Generator using Google OR-Tools.
    Generates a schedule that respects:
    1. Teacher availability (no double booking globally)
    2. Subject periods per week requirement
    3. Daily limits per subject
    """
    
    def __init__(self, class_name: SchoolClass, section: Section, academic_year: AcademicYear):
        self.class_name = class_name
        self.section = section
        self.academic_year = academic_year
        
        # Configuration
        self.days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        self.periods_per_day = 8
        self.num_days = len(self.days)
        self.num_periods = self.periods_per_day
        
        # Data caches
        self.subjects = []
        self.teacher_unavailable_slots = set() # (day_index, period_index, teacher_id)
        
    def generate(self):
        """Main generation method"""
        logger.info(f"Starting auto-generation for {self.class_name} - {self.section}")
        
        # 1. Collect Data
        self._collect_data()
        
        # 2. Build Model
        model = cp_model.CpModel()
        
        # Variables: schedule[(day, period, subject_idx)] = bool
        # If true, that subject is taught at that time
        schedule = {}
        
        # We also need a "No Subject" option for free periods? 
        # Actually, simpler: X[d, p] = subject_index
        # subject_index includes -1 or some value for "Empty/Break"
        
        # Let's map subjects to indices 0..N-1
        # We might have breaks fixed.
        
        # Create variables
        # X[day, period] -> 0..NumSubjects
        # If we use 0 as "Free/Break", and 1..N as subjects.
        
        # Better: boolean vars for each subject assignment
        # x[d, p, s] implies subject s is at day d, period p
        
        for d in range(self.num_days):
            for p in range(1, self.num_periods + 1):
                # Hard constraints for Breaks (e.g. Period 4 is break)
                if p == 4:
                    continue # Skip break period
                    
                for s_idx, subject in enumerate(self.subjects):
                    schedule[(d, p, s_idx)] = model.NewBoolVar(f'sched_{d}_{p}_{s_idx}')

        # 3. Add Constraints
        
        # C1: At most one subject per slot
        for d in range(self.num_days):
            for p in range(1, self.num_periods + 1):
                if p == 4: continue
                model.Add(sum(schedule[(d, p, s_idx)] for s_idx in range(len(self.subjects))) <= 1)

        # C2: Weekly period counts
        for s_idx, subject in enumerate(self.subjects):
            required = subject.periods_per_week
            model.Add(sum(
                schedule[(d, p, s_idx)] 
                for d in range(self.num_days) 
                for p in range(1, self.num_periods + 1) if p != 4
            ) == required)
            
        # C3: Teacher Availability (Global)
        # If teacher T is busy at D, P in ANOTHER class, they cannot be here.
        # We populated self.teacher_unavailable_slots in _collect_data
        for d in range(self.num_days):
            for p in range(1, self.num_periods + 1):
                if p == 4: continue
                
                for s_idx, subject in enumerate(self.subjects):
                    teacher_id = subject.teacher_id
                    if teacher_id:
                        if (d, p, teacher_id) in self.teacher_unavailable_slots:
                            # Force this var to 0
                            model.Add(schedule[(d, p, s_idx)] == 0)

        # C4: Max periods per day per subject (e.g. max 2)
        for s_idx in range(len(self.subjects)):
            for d in range(self.num_days):
                 model.Add(sum(
                    schedule[(d, p, s_idx)] 
                    for p in range(1, self.num_periods + 1) if p != 4
                 ) <= 2)

        # 4. Solve
        solver = cp_model.CpSolver()
        # solver.parameters.log_search_progress = True
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("Solution found!")
            return self._save_solution(solver, schedule)
        else:
            logger.error("No solution found.")
            return None

    def _collect_data(self):
        """Fetch subjects and global teacher availability"""
        # 1. Subjects
        self.subjects = list(ClassSubject.objects.filter(
            class_name=self.class_name,
            academic_year=self.academic_year
        ).select_related('subject', 'teacher'))
        
        if not self.subjects:
            raise ValidationError("No subjects found for this class.")
            
        # 2. Global Teacher Availability
        # Find ALL timetable entries for this academic year, EXCLUDING this class/section
        # (Since we are overwriting this class/section's timetable, we ignore its old entries.
        # But user said "without disturbing present timetable gen". 
        # If they mean "don't change OTHER classes", then yes, we exclude self.
        
        other_timetables = TimeTable.objects.filter(
            academic_year=self.academic_year
        ).exclude(
            class_name=self.class_name,
            section=self.section
        ).select_related('teacher')
        
        for entry in other_timetables:
            if entry.teacher_id:
                # Map day string to index
                if entry.day in self.days:
                    d_idx = self.days.index(entry.day)
                    self.teacher_unavailable_slots.add(
                        (d_idx, entry.period_number, entry.teacher_id)
                    )

    def _add_minutes(self, time_obj, minutes):
        """Add minutes to a time object"""
        from datetime import time
        total_minutes = time_obj.hour * 60 + time_obj.minute + minutes
        return time(total_minutes // 60, total_minutes % 60)

    def _save_solution(self, solver, schedule):
        """Save the solved schedule to DB"""
        from datetime import time
        
        with transaction.atomic():
            # Clear existing
            TimeTable.objects.filter(
                class_name=self.class_name,
                section=self.section,
                academic_year=self.academic_year
            ).delete()
            
            entries = []
            
            # Base start time (should theoretically come from settings)
            start_time_base = time(8, 0) 
            period_duration = 45 # minutes
            
            for d_idx, day_name in enumerate(self.days):
                current_time = start_time_base
                
                # Assembly (Period 0) - Optional, mimicking manual gen
                if day_name != 'SATURDAY':
                     # Skipping assembly creation to avoid complexity for now, can be added later
                     # But we must advance time if assembly exists in school routine
                     # For now, let's assume standard schedule starting at 8:00
                     pass

                for p in range(1, self.num_periods + 1):
                    # Calculate Times
                    p_start = current_time
                    p_end = self._add_minutes(current_time, period_duration)
                    
                    # BREAK (Period 4) - Skip creating entry as per schema constraints
                    if p == 4:
                        current_time = p_end
                        continue

                    # Subject Slot
                    found_s_idx = None
                    for s_idx, subject in enumerate(self.subjects):
                        if solver.Value(schedule[(d_idx, p, s_idx)]):
                            found_s_idx = s_idx
                            break
                    
                    if found_s_idx is not None:
                        subj_obj = self.subjects[found_s_idx]
                        entries.append(TimeTable(
                            class_name=self.class_name,
                            section=self.section,
                            academic_year=self.academic_year,
                            day=day_name,
                            period_number=p,
                            period_type='PRACTICAL' if subj_obj.subject.has_practical else 'LECTURE',
                            subject=subj_obj,
                            teacher=subj_obj.teacher,
                            start_time=p_start,
                            end_time=p_end,
                            room="Class Room" # Default room
                        ))
                    
                    # Advance time
                    current_time = p_end
            
            TimeTable.objects.bulk_create(entries)
            return len(entries)
