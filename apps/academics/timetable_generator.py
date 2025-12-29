# apps/academics/timetable_generator.py
import uuid
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import time, timedelta
from typing import List, Dict, Tuple
import random
from collections import defaultdict

from .models import (
    TimeTable, SchoolClass, Section, ClassSubject,
    AcademicYear, Subject, Holiday
)


class TimetableGenerator:
    """
    Generates timetable based on constraints and availability
    """
    
    def __init__(self, class_name: SchoolClass, section: Section, academic_year: AcademicYear):
        self.class_name = class_name
        self.section = section
        self.academic_year = academic_year
        self.timetable_entries = []
        
        # Configuration
        self.days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        self.periods_per_day = 8  # Adjust based on school
        self.period_duration = 45  # minutes
        self.start_time = time(8, 0)  # 8:00 AM
        
        # Cache data
        self._subjects = None
        self._teachers = None
        self._holidays = None
    
    def generate(self, overwrite=False):
        """
        Generate complete timetable
        """
        if not overwrite and TimeTable.objects.filter(
            class_name=self.class_name,
            section=self.section,
            academic_year=self.academic_year
        ).exists():
            raise ValidationError("Timetable already exists for this class/section")
        
        # Clear existing timetable
        TimeTable.objects.filter(
            class_name=self.class_name,
            section=self.section,
            academic_year=self.academic_year
        ).delete()
        
        # Generate timetable
        self._collect_data()
        self._generate_daily_schedule()
        
        # Save to database
        return self._save_timetable()
    
    def _collect_data(self):
        """Collect required data for generation"""
        # Get subjects for this class
        self._subjects = list(ClassSubject.objects.filter(
            class_name=self.class_name,
            academic_year=self.academic_year
        ).select_related('subject', 'teacher'))
        
        # Get holidays
        self._holidays = list(Holiday.objects.filter(
            academic_year=self.academic_year
        ).values_list('start_date', 'end_date'))
        
        # Validate data
        if not self._subjects:
            raise ValidationError("No subjects found for this class")
    
    def _generate_daily_schedule(self):
        """Generate schedule for each day"""
        for day_index, day in enumerate(self.days):
            daily_periods = self._generate_day_schedule(day)
            self.timetable_entries.extend(daily_periods)
    
    def _generate_day_schedule(self, day: str) -> List[Dict]:
        """Generate schedule for a single day"""
        periods = []
        current_time = self.start_time
        
        # Start with morning assembly on some days
        if day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
            periods.append({
                'day': day,
                'period_number': 0,
                'start_time': current_time,
                'end_time': self._add_minutes(current_time, 15),
                'period_type': 'ASSEMBLY',
                'subject': None,
                'teacher': None,
                'room': 'Assembly Hall'
            })
            current_time = self._add_minutes(current_time, 15)
        
        # Generate academic periods
        for period_num in range(1, self.periods_per_day + 1):
            # Break after specific periods
            if period_num == 4:  # Lunch break
                periods.append({
                    'day': day,
                    'period_number': period_num,
                    'start_time': current_time,
                    'end_time': self._add_minutes(current_time, 45),
                    'period_type': 'BREAK',
                    'subject': None,
                    'teacher': None,
                    'room': ''
                })
                current_time = self._add_minutes(current_time, 45)
                continue
            
            # Get subject for this period
            subject_assignment = self._get_subject_for_period(day, period_num)
            
            if subject_assignment:
                periods.append({
                    'day': day,
                    'period_number': period_num,
                    'start_time': current_time,
                    'end_time': self._add_minutes(current_time, self.period_duration),
                    'period_type': 'PRACTICAL' if subject_assignment.subject.has_practical else 'LECTURE',
                    'subject': subject_assignment,
                    'teacher': subject_assignment.teacher,
                    'room': self._get_room_for_subject(subject_assignment.subject)
                })
            else:
                # Free period or games
                periods.append({
                    'day': day,
                    'period_number': period_num,
                    'start_time': current_time,
                    'end_time': self._add_minutes(current_time, self.period_duration),
                    'period_type': 'GAMES' if day == 'SATURDAY' else 'LECTURE',
                    'subject': None,
                    'teacher': None,
                    'room': 'Playground' if day == 'SATURDAY' else ''
                })
            
            current_time = self._add_minutes(current_time, self.period_duration)
        
        return periods
    
    def _get_subject_for_period(self, day: str, period_num: int):
        """Get appropriate subject for a given period"""
        # Simple round-robin assignment
        # You can implement more complex logic here
        
        # Filter subjects that should be taught on this day
        available_subjects = [
            s for s in self._subjects 
            if s.periods_per_week > 0
        ]
        
        if not available_subjects:
            return None
        
        # Simple algorithm: Assign based on day and period
        day_index = self.days.index(day)
        subject_index = (day_index + period_num) % len(available_subjects)
        
        selected_subject = available_subjects[subject_index]
        
        # Reduce periods count for the week
        selected_subject.periods_per_week -= 1
        
        return selected_subject
    
    def _get_room_for_subject(self, subject: Subject) -> str:
        """Assign room based on subject type"""
        if subject.has_practical:
            return f"Lab {random.randint(1, 5)}"
        elif subject.subject_type == "CO_CURRICULAR":
            return "Activity Room"
        else:
            return f"Room {self.section.room_number}" if self.section.room_number else f"Room {random.randint(1, 20)}"
    
    def _add_minutes(self, time_obj: time, minutes: int) -> time:
        """Add minutes to a time object"""
        total_minutes = time_obj.hour * 60 + time_obj.minute + minutes
        return time(total_minutes // 60, total_minutes % 60)
    
    def _save_timetable(self):
        """Save generated timetable to database"""
        entries = []
        
        for entry in self.timetable_entries:
            timetable_entry = TimeTable(
                class_name=self.class_name,
                section=self.section,
                academic_year=self.academic_year,
                day=entry['day'],
                period_number=entry['period_number'],
                start_time=entry['start_time'],
                end_time=entry['end_time'],
                period_type=entry['period_type'],
                room=entry['room'],
                subject=entry['subject'],
                teacher=entry['teacher'] if entry.get('teacher') else None
            )
            
            # Validate before saving
            timetable_entry.full_clean()
            entries.append(timetable_entry)
        
        # Bulk create
        TimeTable.objects.bulk_create(entries)
        return entries


class TimetableValidator:
    """
    Validates timetable for conflicts and constraints
    """
    
    @staticmethod
    def validate_timetable(class_name: SchoolClass, section: Section, academic_year: AcademicYear):
        """
        Validate existing timetable for conflicts
        """
        timetable_entries = TimeTable.objects.filter(
            class_name=class_name,
            section=section,
            academic_year=academic_year
        ).select_related('teacher', 'subject')
        
        errors = []
        
        # Check for teacher conflicts
        teacher_schedule = defaultdict(list)
        for entry in timetable_entries:
            if entry.teacher:
                key = (entry.day, entry.start_time, entry.teacher_id)
                if key in teacher_schedule:
                    errors.append(
                        f"Teacher {entry.teacher} has overlapping classes on "
                        f"{entry.day} at {entry.start_time}"
                    )
                teacher_schedule[key].append(entry)
        
        # Check for room conflicts
        room_schedule = defaultdict(list)
        for entry in timetable_entries:
            if entry.room:
                key = (entry.day, entry.start_time, entry.room)
                if key in room_schedule:
                    errors.append(
                        f"Room {entry.room} is double-booked on "
                        f"{entry.day} at {entry.start_time}"
                    )
                room_schedule[key].append(entry)
        
        # Check subject distribution
        subject_count = defaultdict(int)
        for entry in timetable_entries:
            if entry.subject:
                subject_count[entry.subject.subject.name] += 1
        
        # Validate against required periods per week
        for subject in ClassSubject.objects.filter(
            class_name=class_name,
            academic_year=academic_year
        ):
            required = subject.periods_per_week
            actual = subject_count.get(subject.subject.name, 0)
            if actual < required:
                errors.append(
                    f"Subject {subject.subject.name} has {actual} periods, "
                    f"but requires {required} periods per week"
                )
        
        return errors
    
    @staticmethod
    def get_teacher_availability(teacher_id: int, academic_year: AcademicYear):
        """
        Get teacher's current timetable
        """
        return TimeTable.objects.filter(
            teacher_id=teacher_id,
            academic_year=academic_year
        ).select_related('class_name', 'section', 'subject')