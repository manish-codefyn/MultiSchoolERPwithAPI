# apps/academics/management/commands/generate_timetable.py
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from apps.academics.models import SchoolClass, Section, AcademicYear
from apps.academics.timetable_generator import TimetableGenerator, TimetableValidator


class Command(BaseCommand):
    help = 'Generate timetable for class/section'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--class',
            dest='class_id',
            type=str,
            help='Class ID'
        )
        parser.add_argument(
            '--section',
            dest='section_id',
            type=str,
            help='Section ID'
        )
        parser.add_argument(
            '--year',
            dest='year_id',
            type=str,
            help='Academic Year ID'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate for all active classes'
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate existing timetable'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing timetable'
        )
    
    def handle(self, *args, **options):
        if options['validate']:
            self.validate_timetable(options)
        elif options['all']:
            self.generate_all(options)
        else:
            self.generate_single(options)
    
    def generate_single(self, options):
        """Generate timetable for single class/section"""
        try:
            class_obj = SchoolClass.objects.get(id=options['class_id'])
            section = Section.objects.get(id=options['section_id'])
            academic_year = AcademicYear.objects.get(id=options['year_id'])
            
            generator = TimetableGenerator(class_obj, section, academic_year)
            entries = generator.generate(overwrite=options['force'])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully generated timetable for '
                    f'{class_obj.name} {section.name}'
                )
            )
            self.stdout.write(f'Created {len(entries)} timetable entries')
            
            # Validate the generated timetable
            errors = TimetableValidator.validate_timetable(
                class_obj, section, academic_year
            )
            if errors:
                self.stdout.write(self.style.WARNING('Validation warnings:'))
                for error in errors:
                    self.stdout.write(f'  - {error}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def generate_all(self, options):
        """Generate timetable for all active classes"""
        academic_year = AcademicYear.objects.get(is_current=True)
        
        sections = Section.objects.filter(
            class_name__is_active=True,
            is_active=True
        ).select_related('class_name')
        
        for section in sections:
            try:
                generator = TimetableGenerator(
                    section.class_name, section, academic_year
                )
                entries = generator.generate(overwrite=options['force'])
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated timetable for {section.class_name.name} {section.name}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed for {section.class_name.name} {section.name}: {str(e)}'
                    )
                )
    
    def validate_timetable(self, options):
        """Validate existing timetable"""
        class_obj = SchoolClass.objects.get(id=options['class_id'])
        section = Section.objects.get(id=options['section_id'])
        academic_year = AcademicYear.objects.get(id=options['year_id'])
        
        errors = TimetableValidator.validate_timetable(
            class_obj, section, academic_year
        )
        
        if not errors:
            self.stdout.write(self.style.SUCCESS('Timetable is valid!'))
        else:
            self.stdout.write(self.style.ERROR('Timetable validation errors:'))
            for error in errors:
                self.stdout.write(f'  • {error}')