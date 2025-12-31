"""
Complete Attendance API Views for School Management System
Includes: QR Scanning, DeepFace Face Recognition, Manual Attendance, and Dashboard
"""

import base64
import io
import tempfile
import os
import re
import csv
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.academics.models import StudentAttendance, SchoolClass, Section
from apps.hr.models import StaffAttendance, Staff
from apps.hostel.models import HostelAttendance
from apps.transportation.models import TransportAttendance
from apps.attendance.api.serializers import (
    StudentAttendanceSerializer, StaffAttendanceSerializer,
    HostelAttendanceSerializer, TransportAttendanceSerializer
)
from apps.students.models import Student

# Optional imports for DeepFace
try:
    import cv2
    import numpy as np
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None
    Image = None

# Import DeepFace service
try:
    from apps.attendance.services.face_recognition_service import deepface_service
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    deepface_service = None

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# STUDENT ATTENDANCE VIEWS
# ============================================================================

class StudentAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = StudentAttendance
    serializer_class = StudentAttendanceSerializer
    search_fields = ['student__first_name', 'student__admission_number']
    filterset_fields = ['date', 'status', 'class_name', 'section', 'student']
    roles_required = ['admin', 'teacher', 'student', 'parent']

class StudentAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = StudentAttendance
    serializer_class = StudentAttendanceSerializer
    roles_required = ['admin', 'teacher']


# ============================================================================
# STAFF ATTENDANCE VIEWS
# ============================================================================

class StaffAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = StaffAttendance
    serializer_class = StaffAttendanceSerializer
    search_fields = ['staff__first_name', 'staff__employee_id']
    filterset_fields = ['date', 'status', 'staff']
    roles_required = ['admin', 'hr_manager', 'principal']

class StaffAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = StaffAttendance
    serializer_class = StaffAttendanceSerializer
    roles_required = ['admin', 'hr_manager', 'principal']


# ============================================================================
# HOSTEL ATTENDANCE VIEWS
# ============================================================================

class HostelAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = HostelAttendance
    serializer_class = HostelAttendanceSerializer
    search_fields = ['student__first_name', 'student__admission_number']
    filterset_fields = ['date', 'status', 'student']
    roles_required = ['admin', 'hostel_warden', 'student', 'parent']

class HostelAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = HostelAttendance
    serializer_class = HostelAttendanceSerializer
    roles_required = ['admin', 'hostel_warden']


# ============================================================================
# TRANSPORT ATTENDANCE VIEWS
# ============================================================================

class TransportAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = TransportAttendance
    serializer_class = TransportAttendanceSerializer
    search_fields = ['student__first_name', 'student__admission_number']
    filterset_fields = ['date', 'status', 'trip_type', 'student']
    roles_required = ['admin', 'transport_manager', 'driver', 'student', 'parent']

class TransportAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = TransportAttendance
    serializer_class = TransportAttendanceSerializer
    roles_required = ['admin', 'transport_manager']


# ============================================================================
# QR CODE ATTENDANCE
# ============================================================================

class MarkQRAttendanceAPIView(APIView):
    """
    Mark attendance via QR Scan.
    Payload: 
      - qr_text: "Admission No: 123" OR "EMP001"
      - type: "student" (default) | "staff" | "transport"
      - trip_type: "PICKUP" | "DROP" (optional, for transport)
    """
    
    def post(self, request, *args, **kwargs):
        qr_text = request.data.get('qr_text', '').strip()
        att_type = request.data.get('type', 'student') 
        
        if not qr_text:
            return Response(
                {"error": "No QR text provided."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------------------------------------
        # 1. STAFF ATTENDANCE
        # ---------------------------------------------------------
        if att_type == 'staff':
            # Assume QR contains Employee ID directly or prefixes
            emp_id = qr_text
            if "Employee ID:" in qr_text:
                emp_id = qr_text.split("Employee ID:")[1].strip()
            
            try:
                staff = Staff.objects.get(employee_id=emp_id)
            except Staff.DoesNotExist:
                return Response(
                    {"error": f"Staff with ID '{emp_id}' not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            today = timezone.now().date()
            now_time = timezone.now().time()
            
            # Create or Get Attendance
            attendance, created = StaffAttendance.objects.get_or_create(
                staff=staff,
                date=today,
                defaults={
                    'status': 'PRESENT',
                    'check_in': now_time,
                    'marked_by': request.user if request.user.is_authenticated else None
                }
            )
            
            if not created:
                if not attendance.check_out:
                    attendance.check_out = now_time
                    attendance.save()
                    msg = f"Check-out marked for {staff.full_name}"
                else:
                    msg = f"Attendance already marked for {staff.full_name}"
            else:
                msg = f"Check-in marked for {staff.full_name}"

            return Response({
                "message": msg,
                "student_name": staff.full_name,  # reuse key for frontend compat
                "status": "PRESENT",
                "photo_url": staff.profile_image.url if staff.profile_image else None,
                "staff": {
                    "name": staff.full_name,
                    "employee_id": staff.employee_id,
                    "photo_url": staff.profile_image.url if staff.profile_image else None,
                    "department": str(staff.department) if staff.department else None
                }
            })

        # ---------------------------------------------------------
        # 2. STUDENT / TRANSPORT ATTENDANCE
        # ---------------------------------------------------------
        # Parse Admission Number
        match = re.search(r'Admission No:\s*([^\s\n]+)', qr_text)
        if not match:
            # Try matching raw if regex fails
            admission_number = qr_text
        else:
            admission_number = match.group(1)

        try:
            student = Student.objects.get(admission_number=admission_number)
            if hasattr(request, 'tenant') and request.tenant and student.tenant != request.tenant:
                return Response(
                    {"error": "Student not found in this school."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Student.DoesNotExist:
            msg = f"Student with Admission No/Roll '{admission_number}' not found."
            return Response({"error": msg}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        
        # TRANSPORT MARKING
        if att_type == 'transport':
            trip_type = request.data.get('trip_type')
            if not trip_type:
                trip_type = 'PICKUP' if timezone.now().hour < 12 else 'DROP'
            
            t_att, created = TransportAttendance.objects.update_or_create(
                student=student,
                date=today,
                trip_type=trip_type,
                defaults={
                    'status': 'PRESENT',
                    'actual_time': timezone.now().time(),
                    'marked_by': request.user if request.user.is_authenticated else None
                }
            )
            photo_doc = student.get_photo()
            photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None

            return Response({
                "message": f"Transport {trip_type} marked for {student.first_name}",
                "student_name": student.full_name,
                "status": "PRESENT",
                "photo_url": photo_url,
                "student": {
                    "name": student.full_name,
                    "class": str(student.current_class),
                    "section": str(student.section),
                    "admission_number": student.admission_number,
                    "photo_url": photo_url
                }
            })

        # HOSTEL ATTENDANCE
        if att_type == 'hostel':
            h_att, created = HostelAttendance.objects.update_or_create(
                student=student,
                date=today,
                defaults={
                    'status': 'PRESENT',
                    'check_in_time': timezone.now().time(),
                    'marked_by': request.user if request.user.is_authenticated else None,
                    'remarks': 'QR Scan'
                }
            )
            photo_doc = student.get_photo()
            photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None

            return Response({
                "message": f"Hostel attendance marked for {student.first_name}",
                "student_name": student.full_name,
                "status": "PRESENT",
                "photo_url": photo_url,
                "student": {
                    "name": student.full_name,
                    "class": str(student.current_class),
                    "section": str(student.section),
                    "admission_number": student.admission_number,
                    "photo_url": photo_url
                }
            })

        # REGULAR STUDENT ATTENDANCE (Default)
        if not student.current_class or not student.section:
            return Response(
                {"error": f"Student {student.first_name} is not assigned to a class or section. Attendance cannot be marked."},
                status=status.HTTP_400_BAD_REQUEST
            )

        att, created = StudentAttendance.objects.update_or_create(
            student=student,
            date=today,
            defaults={
                'status': 'PRESENT',
                'class_name': student.current_class,
                'section': student.section,
                'marked_by': request.user if request.user.is_authenticated else None
            }
        )
        
        photo_doc = student.get_photo()
        photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None

        return Response({
            "message": f"Present marked for {student.first_name}",
            "student_name": student.full_name,
            "roll_number": student.roll_number,
            "status": "PRESENT",
            "photo_url": photo_url,
            "student": {
                "name": student.full_name,
                "class": str(student.current_class),
                "section": str(student.section),
                "admission_number": student.admission_number,
                "photo_url": photo_url
            }
        })


# ============================================================================
# DEEPFACE FACE RECOGNITION ATTENDANCE
# ============================================================================

class DeepFaceBaseView(APIView):
    """
    Base view for all DeepFace recognition operations
    """
    # Authentication and permissions
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        if not DEEPFACE_AVAILABLE:
            logger.warning("DeepFace service not available. Install with: pip install deepface opencv-python")
    
    def validate_image_input(self, image_data, image_file):
        """Validate image input"""
        if not image_data and not image_file:
            raise ValueError("Send either 'image' (base64) or 'image_file' (multipart form)")
        
        # Validate base64
        if image_data:
            if not isinstance(image_data, str):
                raise ValueError("Image data must be a base64 string")
        
        # Validate file
        if image_file:
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
            ext = os.path.splitext(image_file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValueError(f"Allowed types: {', '.join(valid_extensions)}")
            
            # Validate size (max 10MB)
            max_size = 10 * 1024 * 1024
            if image_file.size > max_size:
                raise ValueError(f"Maximum size is {max_size/1024/1024}MB")
        
        return True
    
    def process_image(self, image_data, image_file):
        """Process image input and return file path"""
        temp_file_path = None
        
        try:
            if image_file:
                # Handle uploaded file
                temp_file_path = self._save_uploaded_file(image_file)
            elif image_data:
                # Handle base64 image
                temp_file_path = self._process_base64_image(image_data)
            
            # Verify image is valid
            self._verify_image(temp_file_path)
            
            return temp_file_path
            
        except Exception as e:
            # Cleanup on error
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise
    
    def _save_uploaded_file(self, uploaded_file):
        """Save uploaded file to temporary location"""
        temp_dir = tempfile.gettempdir()
        filename = f"deepface_{int(timezone.now().timestamp())}_{uploaded_file.name}"
        temp_path = os.path.join(temp_dir, filename)
        
        with open(temp_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        return temp_path
    
    def _process_base64_image(self, image_data):
        """Process base64 image data"""
        # Extract base64 data
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        try:
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Verify it's a valid image
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()
            
            # Re-open for processing
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to temporary file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"deepface_{int(timezone.now().timestamp())}.jpg")
            
            image.save(temp_path, 'JPEG', quality=85)
            
            return temp_path
            
        except Exception as e:
            raise ValueError(f"Invalid base64 image: {str(e)}")
    
    def _verify_image(self, image_path):
        """Verify image is valid and readable"""
        try:
            # Try to read with OpenCV
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image file")
            
            # Check image dimensions
            height, width = img.shape[:2]
            if height < 50 or width < 50:
                raise ValueError("Image dimensions too small (min 50x50)")
            
            if height > 4000 or width > 4000:
                raise ValueError("Image dimensions too large (max 4000x4000)")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Invalid image: {str(e)}")
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary file"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")


class MarkDeepFaceAttendanceAPIView(DeepFaceBaseView):
    """
    Mark attendance using DeepFace face recognition
    Replaces the old MarkFaceAttendanceAPIView
    """
    
    def post(self, request):
        """
        Mark attendance via DeepFace face recognition
        Payload: {
            "image": "base64_string",  # OR
            "image_file": File,
            "type": "student|staff|transport|hostel",
            "trip_type": "PICKUP|DROP",
            "min_confidence": 0.5  # Optional
        }
        """
        # Check if DeepFace is available
        if not DEEPFACE_AVAILABLE:
            return Response(
                {
                    "error": "DeepFace service not available",
                    "detail": "Install required packages: pip install deepface opencv-python"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Extract parameters
        image_data = request.data.get('image')
        image_file = request.FILES.get('image_file')
        att_type = request.data.get('type', 'student')
        trip_type = request.data.get('trip_type')
        min_confidence = float(request.data.get('min_confidence', 0.5))
        
        # Validate inputs
        try:
            self.validate_image_input(image_data, image_file)
        except ValueError as e:
            return Response(
                {"error": "Invalid input", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate attendance type
        valid_types = ['student', 'staff', 'transport', 'hostel']
        if att_type not in valid_types:
            return Response(
                {
                    "error": "Invalid attendance type",
                    "detail": f"Valid types: {', '.join(valid_types)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        temp_file_path = None
        
        try:
            # Process image
            temp_file_path = self.process_image(image_data, image_file)
            
            # Perform face recognition
            recognition_result, message, confidence, distance = deepface_service.recognize_face(
                image_path=temp_file_path,
                min_confidence=min_confidence
            )
            
            if not recognition_result:
                # Provide helpful error messages
                if "No face detected" in message:
                    error_detail = "No face was detected in the image. Please ensure face is clearly visible and well-lit."
                elif "No matching face" in message:
                    error_detail = f"Face not recognized. Confidence: {confidence:.2%}, Distance: {distance:.4f}"
                else:
                    error_detail = message
                
                return Response({
                    "error": "Face recognition failed",
                    "detail": error_detail,
                    "confidence": confidence,
                    "distance": distance,
                    "threshold": deepface_service.threshold
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Mark attendance
            result = self.mark_attendance(
                request, 
                recognition_result, 
                att_type, 
                trip_type,
                confidence,
                distance
            )
            
            # Add recognition details
            result.update({
                'recognition_confidence': confidence,
                'recognition_distance': distance,
                'recognition_threshold': deepface_service.threshold,
                'recognition_model': deepface_service.model_name,
                'recognition_metric': deepface_service.distance_metric
            })
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"DeepFace attendance error: {str(e)}", exc_info=True)
            return Response({
                "error": "Internal server error",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        finally:
            # Cleanup temp file
            if temp_file_path:
                self.cleanup_temp_file(temp_file_path)
    
    @transaction.atomic
    def mark_attendance(self, request, person_data, att_type, trip_type, confidence, distance):
        """Mark attendance for recognized person"""
        person_id = person_data['id']
        person_type = person_data['type']
        
        # Validate person type vs attendance type
        if person_type == 'staff' and att_type != 'staff':
            return Response({
                "error": "Person type mismatch",
                "detail": "Recognized staff member but requested student attendance"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if person_type == 'student' and att_type == 'staff':
            return Response({
                "error": "Person type mismatch",
                "detail": "Recognized student but requested staff attendance"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        now_time = timezone.now().time()
        
        # Get person object
        person = self.get_person_object(person_type, person_id)
        if isinstance(person, Response):
            return person
        
        # Mark attendance based on type
        if att_type == 'staff':
            return self.mark_staff_attendance(request, person, today, now_time, confidence, distance)
        elif att_type == 'transport':
            return self.mark_transport_attendance(request, person, today, now_time, trip_type, confidence, distance)
        elif att_type == 'hostel':
            return self.mark_hostel_attendance(request, person, today, now_time, confidence, distance)
        else:  # student
            return self.mark_student_attendance(request, person, today, confidence, distance)
    
    def get_person_object(self, person_type, person_id):
        """Get person object from database"""
        try:
            if person_type == 'student':
                return Student.objects.select_related(
                    'current_class', 'section'
                ).get(id=person_id)
            else:  # staff
                return Staff.objects.select_related(
                    'user', 'department', 'designation'
                ).get(id=person_id)
        except (Student.DoesNotExist, Staff.DoesNotExist):
            return Response({
                'error': 'Person not found',
                'detail': f'{person_type.title()} with ID {person_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def mark_student_attendance(self, request, student, date, confidence, distance):
        """Mark student attendance"""
        # Check for existing attendance today
        existing = StudentAttendance.objects.filter(
            student=student,
            date=date
        ).first()
        
        if existing:
            # Update existing attendance
            existing.status = 'PRESENT'
            existing.remarks = f"DeepFace Recognition (Confidence: {confidence:.2%}, Distance: {distance:.4f})"
            existing.marked_by = request.user
            existing.method = 'DEEPFACE_RECOGNITION'
            existing.save()
            created = False
            attendance = existing
        else:
            # Create new attendance
            attendance = StudentAttendance.objects.create(
                student=student,
                date=date,
                status='PRESENT',
                class_name=student.current_class,
                section=student.section,
                remarks=f"DeepFace Recognition (Confidence: {confidence:.2%}, Distance: {distance:.4f})",
                marked_by=request.user,
                method='DEEPFACE_RECOGNITION',
                recognition_data={
                    'confidence': confidence,
                    'distance': distance,
                    'model': deepface_service.model_name,
                    'metric': deepface_service.distance_metric,
                    'threshold': deepface_service.threshold
                }
            )
            created = True
        
        # Get photo URL
        photo_doc = student.get_photo()
        photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None
        
        return {
            'success': True,
            'message': f'Attendance marked for {student.first_name}',
            'student_name': student.full_name,
            'roll_number': student.roll_number,
            'admission_number': student.admission_number,
            'status': 'PRESENT',
            'photo_url': photo_url,
            'created': created,
            'timestamp': timezone.now().isoformat()
        }
    
    def mark_staff_attendance(self, request, staff, date, time, confidence, distance):
        """Mark staff attendance"""
        attendance = StaffAttendance.objects.filter(
            staff=staff,
            date=date
        ).first()
        
        action = None
        created = False
        
        if attendance:
            if not attendance.check_out:
                # Mark check-out
                attendance.check_out = time
                attendance.remarks = f"DeepFace Check-out (Confidence: {confidence:.2%})"
                attendance.save()
                action = 'check-out'
            else:
                action = 'already marked'
        else:
            # Mark check-in
            attendance = StaffAttendance.objects.create(
                staff=staff,
                date=date,
                status='PRESENT',
                check_in=time,
                remarks=f"DeepFace Check-in (Confidence: {confidence:.2%}, Distance: {distance:.4f})",
                marked_by=request.user,
                method='DEEPFACE_RECOGNITION',
                recognition_data={
                    'confidence': confidence,
                    'distance': distance,
                    'model': deepface_service.model_name
                }
            )
            action = 'check-in'
            created = True
        
        photo_url = staff.profile_image.url if staff.profile_image else None
        
        return {
            'success': True,
            'message': f'{action.capitalize()} marked for {staff.full_name}',
            'staff_name': staff.full_name,
            'employee_id': staff.employee_id,
            'status': 'PRESENT',
            'photo_url': photo_url,
            'action': action,
            'check_in': str(attendance.check_in) if attendance.check_in else None,
            'check_out': str(attendance.check_out) if attendance.check_out else None,
            'created': created,
            'timestamp': timezone.now().isoformat()
        }
    
    def mark_transport_attendance(self, request, student, date, time, trip_type, confidence, distance):
        """Mark transport attendance"""
        if not trip_type:
            trip_type = 'PICKUP' if timezone.now().hour < 12 else 'DROP'
        
        attendance, created = TransportAttendance.objects.update_or_create(
            student=student,
            date=date,
            trip_type=trip_type,
            defaults={
                'status': 'PRESENT',
                'actual_time': time,
                'remarks': f"DeepFace Recognition (Confidence: {confidence:.2%})",
                'marked_by': request.user,
                'method': 'DEEPFACE_RECOGNITION',
                'recognition_data': {
                    'confidence': confidence,
                    'distance': distance
                }
            }
        )
        
        photo_doc = student.get_photo()
        photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None
        
        return {
            'success': True,
            'message': f'Transport {trip_type} marked for {student.first_name}',
            'student_name': student.full_name,
            'status': 'PRESENT',
            'photo_url': photo_url,
            'trip_type': trip_type,
            'created': created,
            'timestamp': timezone.now().isoformat()
        }
    
    def mark_hostel_attendance(self, request, student, date, time, confidence, distance):
        """Mark hostel attendance"""
        attendance, created = HostelAttendance.objects.update_or_create(
            student=student,
            date=date,
            defaults={
                'status': 'PRESENT',
                'check_in_time': time,
                'remarks': f"DeepFace Recognition (Confidence: {confidence:.2%})",
                'marked_by': request.user,
                'method': 'DEEPFACE_RECOGNITION'
            }
        )
        
        photo_doc = student.get_photo()
        photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None
        
        return {
            'success': True,
            'message': f'Hostel attendance marked for {student.first_name}',
            'student_name': student.full_name,
            'status': 'PRESENT',
            'photo_url': photo_url,
            'created': created,
            'timestamp': timezone.now().isoformat()
        }


class DeepFaceBatchRecognitionAPIView(DeepFaceBaseView):
    """
    Batch face recognition for multiple faces in one image
    """
    
    def post(self, request):
        """
        Process multiple faces in a single image
        Payload: {
            "image_file": File,
            "type": "student",  # Currently students only
            "class_id": "uuid",  # Optional filter
            "min_confidence": 0.5
        }
        """
        # Check if DeepFace is available
        if not DEEPFACE_AVAILABLE:
            return Response(
                {
                    "error": "DeepFace service not available",
                    "detail": "Install required packages: pip install deepface opencv-python"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        image_file = request.FILES.get('image_file')
        att_type = request.data.get('type', 'student')
        class_id = request.data.get('class_id')
        min_confidence = float(request.data.get('min_confidence', 0.5))
        
        if not image_file:
            return Response(
                {"error": "No image file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if att_type != 'student':
            return Response(
                {"error": "Batch processing currently supports students only"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        temp_file_path = None
        
        try:
            # Process image
            temp_file_path = self.process_image(None, image_file)
            
            # Recognize multiple faces
            recognized_faces, message = deepface_service.recognize_multiple_faces(temp_file_path)
            
            # Filter by class if specified
            if class_id and recognized_faces:
                recognized_faces = [
                    f for f in recognized_faces 
                    if f.get('class_id') == class_id
                ]
            
            # Mark attendance for each recognized face
            results = []
            successful = 0
            
            for face_data in recognized_faces:
                try:
                    if face_data.get('confidence', 0) >= min_confidence:
                        result = self.mark_single_attendance(request, face_data)
                        if result.get('success'):
                            successful += 1
                        results.append(result)
                    else:
                        results.append({
                            'student': face_data.get('name', 'Unknown'),
                            'success': False,
                            'error': 'Low confidence',
                            'confidence': face_data.get('confidence', 0)
                        })
                except Exception as e:
                    results.append({
                        'student': face_data.get('name', 'Unknown'),
                        'success': False,
                        'error': str(e),
                        'confidence': face_data.get('confidence', 0)
                    })
            
            return Response({
                "success": True,
                "message": message,
                "total_faces_detected": len(recognized_faces),
                "successfully_marked": successful,
                "results": results
            })
            
        except Exception as e:
            logger.error(f"Batch face recognition error: {str(e)}", exc_info=True)
            return Response({
                "error": "Batch processing failed",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if temp_file_path:
                self.cleanup_temp_file(temp_file_path)
    
    def mark_single_attendance(self, request, face_data):
        """Mark attendance for single recognized face"""
        if face_data['type'] != 'student':
            raise ValueError("Only student attendance supported")
        
        student = Student.objects.get(id=face_data['id'])
        confidence = face_data.get('confidence', 0)
        
        attendance, created = StudentAttendance.objects.update_or_create(
            student=student,
            date=timezone.now().date(),
            defaults={
                'status': 'PRESENT',
                'class_name': student.current_class,
                'section': student.section,
                'remarks': f"Batch DeepFace Recognition (Confidence: {confidence:.2%})",
                'marked_by': request.user,
                'method': 'DEEPFACE_BATCH'
            }
        )
        
        photo_doc = student.get_photo()
        photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None
        
        return {
            'name': student.full_name,
            'admission_number': student.admission_number,
            'status': 'PRESENT',
            'confidence': confidence,
            'photo_url': photo_url,
            'success': True
        }


# ============================================================================
# BULK / MANUAL ATTENDANCE APIS
# ============================================================================

class StudentListByClassAPIView(APIView):
    """
    Get list of students for a class/section with their attendance status for TODAY.
    Query Params: class_id, section_id (optional)
    """
    
    def get(self, request):
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')

        if not class_id:
            return Response(
                {"error": "class_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
             
        students = Student.objects.filter(current_class_id=class_id, status='ACTIVE')
        if section_id:
            students = students.filter(section_id=section_id)
            
        students = students.order_by('roll_number', 'first_name')
        
        # Get today's attendance map
        today = timezone.now().date()
        attendance_map = {
            att.student_id: att.status 
            for att in StudentAttendance.objects.filter(date=today, student__in=students)
        }

        data = []
        for s in students:
            # Determine status: Default to ABSENT or PRESENT? 
            # Usually if no record, it's "Not Marked" (Gray).
            # If user clicks, it becomes Present (Green).
            current_status = attendance_map.get(s.id, 'NOT_MARKED')
            
            # Simple photo URL logic
            photo_doc = s.get_photo()
            photo_url = photo_doc.file.url if photo_doc and photo_doc.file else None

            data.append({
                'id': s.id,
                'name': s.full_name,
                'roll_number': s.roll_number,
                'admission_number': s.admission_number,
                'photo_url': photo_url,
                'status': current_status
            })
            
        return Response(data)


class BulkAttendanceUpdateAPIView(APIView):
    """
    Update attendance for a specific student or bulk.
    Payload: { "student_id": "uuid", "status": "PRESENT" }
    """
    
    def post(self, request):
        student_id = request.data.get('student_id')
        new_status = request.data.get('status')  # PRESENT, ABSENT
        date_str = request.data.get('date')
        
        if not student_id or not new_status:
            return Response(
                {"error": "student_id and status required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        today = timezone.now().date()
        if date_str:
            try:
                today = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format (YYYY-MM-DD)"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        student = get_object_or_404(Student, id=student_id)
        
        # Update or Create
        attendance, created = StudentAttendance.objects.update_or_create(
            student=student, 
            date=today,
            defaults={
                'status': new_status,
                'marked_by': request.user if request.user.is_authenticated else None,
                'class_name': student.current_class,
                'section': student.section,
                'tenant': student.tenant if hasattr(student, 'tenant') else None
            }
        )
        
        return Response({
            "success": True,
            "message": f"Attendance marked as {new_status} for {student.first_name}",
            "created": created,
            "attendance_id": str(attendance.id)
        })


# ============================================================================
# DASHBOARD & REPORTING APIs
# ============================================================================

class AttendanceStatsAPIView(APIView):
    """
    GET /api/v1/attendance/stats/
    Returns aggregated stats for a specific date (defaults to today).
    Filters: class_id, section_id
    """
    
    def get(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format (YYYY-MM-DD)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = timezone.now().date()
            
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        
        # Base Query
        queryset = StudentAttendance.objects.filter(date=target_date)
        
        # Tenant Filter
        if hasattr(request, 'tenant') and request.tenant:
            queryset = queryset.filter(tenant=request.tenant)
            
        if class_id:
            queryset = queryset.filter(class_name_id=class_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)
            
        # Aggregation
        total = queryset.count()
        present = queryset.filter(status='PRESENT').count()
        absent = queryset.filter(status='ABSENT').count()
        late = queryset.filter(status='LATE').count()
        half_day = queryset.filter(status='HALFDAY').count()
        
        return Response({
            "date": target_date,
            "total_marked": total,
            "present": present,
            "absent": absent,
            "late": late,
            "half_day": half_day,
            "attendance_percentage": round((present / total * 100), 1) if total > 0 else 0.0
        })


class AttendanceHistoryListAPIView(BaseListCreateAPIView):
    """
    GET /api/v1/attendance/history/
    Filterable history of student attendance.
    """
    model = StudentAttendance
    serializer_class = StudentAttendanceSerializer
    search_fields = ['student__first_name', 'student__admission_number', 'remarks']
    filterset_fields = ['date', 'status', 'class_name', 'section', 'student']
    roles_required = ['admin', 'teacher', 'principal', 'parent', 'student']
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Date Range Filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
            
        # Role-based restriction fallback
        user = self.request.user
        if user.role == 'student' and hasattr(user, 'student_profile'):
            qs = qs.filter(student=user.student_profile)
        elif user.role == 'parent':
            # TODO: Filter by parent's children if applicable
            pass
             
        return qs.order_by('-date', 'student__first_name')


class AttendanceExportAPIView(APIView):
    """
    GET /api/v1/attendance/export/
    Export attendance records to CSV.
    """
    
    def get(self, request):
        # Reuse filter logic (simplified)
        queryset = StudentAttendance.objects.all()
        if hasattr(request, 'tenant') and request.tenant:
            queryset = queryset.filter(tenant=request.tenant)
            
        # Apply filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        class_id = request.query_params.get('class_id')
        
        if start_date: 
            queryset = queryset.filter(date__gte=start_date)
        if end_date: 
            queryset = queryset.filter(date__lte=end_date)
        if class_id: 
            queryset = queryset.filter(class_name_id=class_id)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{timezone.now().date()}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Student Name', 'Admission No', 'Class', 'Status', 'Remarks'])

        for att in queryset.select_related('student', 'class_name'):
            writer.writerow([
                att.date,
                att.student.full_name if att.student else 'N/A',
                att.student.admission_number if att.student else 'N/A',
                f"{att.class_name.name} {att.section.name}" if att.class_name else 'N/A',
                att.status,
                att.remarks
            ])

        return response


# ============================================================================
# DASHBOARD API VIEW
# ============================================================================

class AttendanceDashboardAPIView(APIView):
    """
    Comprehensive dashboard API that returns:
    - Stats for all attendance types (Student, Staff, Hostel, Transport)
    - Quick action links
    - Recent attendance records
    """
    
    def get(self, request):
        from django.urls import reverse
        today = timezone.now().date()
        
        # Student Stats
        student_total = Student.objects.filter(status='ACTIVE').count()
        student_present = StudentAttendance.objects.filter(
            date=today, status='PRESENT'
        ).count()
        student_absent = StudentAttendance.objects.filter(
            date=today, status='ABSENT'
        ).count()
        student_late = StudentAttendance.objects.filter(
            date=today, status='LATE'
        ).count()
        student_percentage = (student_present / student_total * 100) if student_total > 0 else 0
        
        # Staff Stats
        staff_total = Staff.objects.filter(employment_status='ACTIVE').count()
        staff_present = StaffAttendance.objects.filter(
            date=today, status='PRESENT'
        ).count()
        staff_absent = StaffAttendance.objects.filter(
            date=today, status='ABSENT'
        ).count()
        staff_late = StaffAttendance.objects.filter(
            date=today, status='LATE'
        ).count()
        staff_percentage = (staff_present / staff_total * 100) if staff_total > 0 else 0
        
        # Hostel Stats (students with hostel allocation)
        hostel_total = Student.objects.filter(status='ACTIVE', hostel_allocation__isnull=False).count()
        hostel_present = HostelAttendance.objects.filter(
            date=today, status='PRESENT'
        ).count()
        hostel_absent = HostelAttendance.objects.filter(
            date=today, status='ABSENT'
        ).count()
        hostel_late = HostelAttendance.objects.filter(
            date=today, status='LATE'
        ).count()
        hostel_percentage = (hostel_present / hostel_total * 100) if hostel_total > 0 else 0
        
        # Transport Stats (students with transport allocation)
        transport_total = Student.objects.filter(status='ACTIVE', transport_allocation__isnull=False).count()
        transport_present = TransportAttendance.objects.filter(
            date=today, status='PRESENT'
        ).count()
        transport_absent = TransportAttendance.objects.filter(
            date=today, status='ABSENT'
        ).count()
        transport_late = TransportAttendance.objects.filter(
            date=today, status='LATE'
        ).count()
        transport_percentage = (transport_present / transport_total * 100) if transport_total > 0 else 0
        
        # Recent Attendance (last 10 records across all types)
        recent_student = list(StudentAttendance.objects.filter(date=today).select_related('student')[:5])
        recent_staff = list(StaffAttendance.objects.filter(date=today).select_related('staff')[:5])
        
        recent_records = []
        for att in recent_student:
            recent_records.append({
                'id': str(att.id),
                'type': 'student',
                'student_name': att.student.full_name,
                'class_name': str(att.class_name) if att.class_name else '',
                'date': str(att.date),
                'status': att.status,
                'created_at': att.created_at.isoformat() if hasattr(att, 'created_at') else None,
            })
        
        for att in recent_staff:
            recent_records.append({
                'id': str(att.id),
                'type': 'staff',
                'student_name': att.staff.full_name,
                'class_name': att.staff.department.name if att.staff.department else '',
                'date': str(att.date),
                'status': att.status,
                'check_in': str(att.check_in) if att.check_in else None,
                'check_out': str(att.check_out) if att.check_out else None,
            })
        
        # Sort by created_at if available
        recent_records.sort(key=lambda x: x.get('created_at') or x.get('check_in') or '', reverse=True)
        
        # Add DeepFace endpoints if available
        face_scan_endpoints = {}
        if DEEPFACE_AVAILABLE:
            face_scan_endpoints = {
                'student': reverse('mark-deepface-attendance'),
                'staff': reverse('mark-deepface-attendance'),
                'hostel': reverse('mark-deepface-attendance'),
                'transport': reverse('mark-deepface-attendance'),
                'batch': reverse('deepface-batch-recognition'),
            }
        else:
            face_scan_endpoints = {
                'student': reverse('mark-face-attendance'),
                'staff': reverse('mark-face-attendance'),
                'hostel': reverse('mark-face-attendance'),
                'transport': reverse('mark-face-attendance'),
            }
        
        return Response({
            'stats': {
                'student': {
                    'total': student_total,
                    'present': student_present,
                    'absent': student_absent,
                    'late': student_late,
                    'percentage': round(student_percentage, 1),
                },
                'staff': {
                    'total': staff_total,
                    'present': staff_present,
                    'absent': staff_absent,
                    'late': staff_late,
                    'percentage': round(staff_percentage, 1),
                },
                'hostel': {
                    'total': hostel_total,
                    'present': hostel_present,
                    'absent': hostel_absent,
                    'late': hostel_late,
                    'percentage': round(hostel_percentage, 1),
                },
                'transport': {
                    'total': transport_total,
                    'present': transport_present,
                    'absent': transport_absent,
                    'late': transport_late,
                    'percentage': round(transport_percentage, 1),
                },
            },
            'quick_actions': {
                'qr_scan': {
                    'student': reverse('mark-qr-attendance'),
                    'staff': reverse('mark-qr-attendance'),
                    'hostel': reverse('mark-qr-attendance'),
                    'transport': reverse('mark-qr-attendance'),
                },
                'face_scan': face_scan_endpoints,
                'manual_entry': reverse('student-attendance-list'),
                'view_records': {
                    'student': reverse('student-attendance-list'),
                    'staff': reverse('staff-attendance-list'),
                    'hostel': reverse('hostel-attendance-list'),
                    'transport': reverse('transport-attendance-list'),
                },
            },
            'recent_attendance': recent_records[:10],
            'deepface_available': DEEPFACE_AVAILABLE,
        })


# ============================================================================
# LEGACY FACE RECOGNITION VIEW (For backward compatibility)
# ============================================================================

class MarkFaceAttendanceAPIView(APIView):
    """
    Legacy face recognition view - redirects to DeepFace if available
    Otherwise uses simplified matching
    """
    
    def post(self, request):
        """
        Face recognition attendance marking
        Uses DeepFace if available, otherwise falls back to simple matching
        """
        # Check if DeepFace is available
        if DEEPFACE_AVAILABLE:
            # Redirect to DeepFace view
            deepface_view = MarkDeepFaceAttendanceAPIView()
            return deepface_view.post(request)
        
        # Fallback to simple matching (original code)
        image_data = request.data.get('image')
        att_type = request.data.get('type', 'student')
        trip_type = request.data.get('trip_type')
        
        if not image_data:
            return Response(
                {"error": "No image provided. Please capture a photo."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simplified approach: Try to match based on available photos
        try:
            if att_type == 'staff':
                candidates = []
                # efficient query to get staff with photos
                # Include ONBOARDING/PROBATION for testing
                staff_qs = Staff.objects.filter(
                    employment_status__in=['ACTIVE', 'ONBOARDING', 'PROBATION']
                ).select_related('user').prefetch_related('documents')
                
                logger.info(f"Checking {staff_qs.count()} staff members for photos")
                
                for s in staff_qs:
                    has_photo = False
                    # Check profile image (if user model has avatar/profile_image)
                    if s.profile_image:
                        has_photo = True
                    elif hasattr(s, 'user') and s.user and hasattr(s.user, 'avatar') and s.user.avatar:
                        has_photo = True
                    # Check documents
                    elif s.documents.filter(document_type='PHOTOGRAPH').exists():
                        has_photo = True
                    
                    if has_photo:
                        candidates.append(s)
                
                if not candidates:
                    return Response({
                        "error": "No staff members with photos found in the system.",
                        "suggestion": "Please ensure staff members have profile photos uploaded (Document type: Photograph)."
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Use first candidate (simplified)
                matched_object = candidates[0] if candidates else None
            else:
                # Student, Hostel, or Transport
                candidates = []
                # Efficient query for students with photos and required academic info
                student_qs = Student.objects.filter(
                    status__in=['ACTIVE', 'TRANSFERRED']
                ).select_related('current_class', 'section')
                
                for s in student_qs:
                    # Verify student has required class info for attendance
                    if not s.current_class:
                        continue
                        
                    if s.get_photo():
                        candidates.append(s)
                
                if not candidates:
                    return Response({
                        "error": "No students with photos found in the system.",
                        "suggestion": "Please ensure students have profile photos and are assigned to a class."
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Use first candidate (simplified)
                matched_object = candidates[0] if candidates else None
            
            if not matched_object:
                return Response({
                    "error": "No matching person found.",
                    "suggestion": "Please ensure the person's photo is in the system."
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Mark attendance for found object
            today = timezone.now().date()
            msg_prefix = "Face Recognition: "
            
            if att_type == 'staff':
                # Obj is Staff
                attendance, created = StaffAttendance.objects.get_or_create(
                    staff=matched_object,
                    date=today,
                    defaults={
                        'status': 'PRESENT',
                        'check_in': timezone.now().time(),
                        'remarks': 'Face Recognition',
                        'marked_by': request.user if request.user.is_authenticated else None
                    }
                )
                
                # Get staff photo from Document model (PHOTOGRAPH type)
                photo_url = None
                try:
                    photo_doc = matched_object.documents.filter(document_type='PHOTOGRAPH').first()
                    if photo_doc and photo_doc.file:
                        photo_url = photo_doc.file.url
                    elif matched_object.profile_image:
                        photo_url = matched_object.profile_image.url
                except Exception:
                    if matched_object.profile_image:
                        photo_url = matched_object.profile_image.url
                
                return Response({
                    "message": f"Attendance marked for {matched_object.full_name}",
                    "student_name": matched_object.full_name,
                    "status": "PRESENT",
                    "photo_url": photo_url
                })
                
            elif att_type == 'transport':
                # Obj is Student
                trip = trip_type or ('PICKUP' if timezone.now().hour < 12 else 'DROP')
                TransportAttendance.objects.update_or_create(
                    student=matched_object,
                    date=today,
                    trip_type=trip,
                    defaults={
                        'status': 'PRESENT',
                        'actual_time': timezone.now().time(),
                        'remarks': 'Face Recognition',
                        'marked_by': request.user if request.user.is_authenticated else None
                    }
                )
                return Response({
                    "message": f"Transport {trip} marked for {matched_object.first_name}",
                    "student_name": matched_object.full_name,
                    "status": "PRESENT",
                    "photo_url": matched_object.get_photo().file.url if matched_object.get_photo() else None
                })
                
            elif att_type == 'hostel':
                # Obj is Student - Mark Hostel Attendance
                HostelAttendance.objects.update_or_create(
                    student=matched_object,
                    date=today,
                    defaults={
                        'status': 'PRESENT',
                        'check_in_time': timezone.now().time(),
                        'remarks': 'Face Recognition',
                        'marked_by': request.user if request.user.is_authenticated else None
                    }
                )
                return Response({
                    "message": f"Hostel attendance marked for {matched_object.first_name}",
                    "student_name": matched_object.full_name,
                    "status": "PRESENT",
                    "photo_url": matched_object.get_photo().file.url if matched_object.get_photo() else None
                })
                
            else:
                # Student
                StudentAttendance.objects.update_or_create(
                    student=matched_object,
                    date=today,
                    defaults={
                        'status': 'PRESENT',
                        'class_name': matched_object.current_class,
                        'section': matched_object.section,
                        'remarks': f"{msg_prefix}Face Scan",
                        'marked_by': request.user if request.user.is_authenticated else None
                    }
                )
                return Response({
                    "message": f"{msg_prefix}Marked Present: {matched_object.first_name}",
                    "student_name": matched_object.full_name,
                    "status": "PRESENT",
                    "photo_url": matched_object.get_photo().file.url if matched_object.get_photo() else None
                })
                
        except Exception as e:
            return Response({
                "error": f"Face recognition failed: {str(e)}",
                "suggestion": "Please try again or contact support."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)