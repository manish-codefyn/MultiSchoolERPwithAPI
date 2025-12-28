"""
Production-grade face recognition service using DeepFace
Simpler installation and maintenance than dlib/face_recognition
"""

import os
import json
import numpy as np
import cv2
import pickle
from deepface import DeepFace
from deepface.commons import functions, distance as dst
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from apps.students.models import Student
from apps.hr.models import Staff
import logging
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class DeepFaceRecognitionService:
    """Advanced face recognition service using DeepFace with multiple model support"""
    
    _instance = None
    _lock = False
    
    # Available models in DeepFace
    AVAILABLE_MODELS = [
        'VGG-Face',  # Default - Good accuracy
        'Facenet',   # Best accuracy
        'OpenFace',  # Fast
        'DeepFace',  # Good balance
        'DeepID',    # Small size
        'ArcFace',   # State of the art
        'SFace'      # Lightweight
    ]
    
    # Available distance metrics
    AVAILABLE_METRICS = ['cosine', 'euclidean', 'euclidean_l2']
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._lock:
            # Configuration
            self.model_name = getattr(settings, 'DEEPFACE_MODEL', 'Facenet')
            self.distance_metric = getattr(settings, 'DEEPFACE_METRIC', 'cosine')
            self.threshold = getattr(settings, 'DEEPFACE_THRESHOLD', 0.4)
            
            # Cache keys
            self.encodings_cache_key = f'deepface_encodings_{self.model_name}'
            self.metadata_cache_key = f'deepface_metadata_{self.model_name}'
            self.last_trained_key = 'deepface_last_trained'
            
            # Initialize
            self.known_face_encodings = []
            self.known_face_metadata = []
            self.encoding_cache = {}  # For quick lookup
            
            # Load pre-trained model
            try:
                logger.info(f"Initializing DeepFace with model: {self.model_name}")
                # Pre-load model for faster inference
                self.model = DeepFace.build_model(self.model_name)
                self.input_shape = functions.find_input_shape(self.model)
                logger.info(f"Model loaded successfully. Input shape: {self.input_shape}")
            except Exception as e:
                logger.error(f"Failed to load DeepFace model: {str(e)}")
                self.model = None
            
            self._lock = True
            self.load_or_train_encodings()
    
    def get_model_info(self):
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'distance_metric': self.distance_metric,
            'threshold': self.threshold,
            'input_shape': self.input_shape if hasattr(self, 'input_shape') else None,
            'available_models': self.AVAILABLE_MODELS,
            'available_metrics': self.AVAILABLE_METRICS
        }
    
    @transaction.atomic
    def load_or_train_encodings(self):
        """Load existing encodings or train new ones"""
        cached_data = cache.get(self.encodings_cache_key)
        cached_metadata = cache.get(self.metadata_cache_key)
        
        if cached_data and cached_metadata and self._validate_cache_data(cached_data, cached_metadata):
            self.known_face_encodings = cached_data
            self.known_face_metadata = cached_metadata
            self._build_encoding_cache()
            
            logger.info(f"Loaded {len(self.known_face_encodings)} face encodings from cache")
            logger.info(f"Model: {self.model_name}, Threshold: {self.threshold}")
        else:
            logger.info("Cache invalid or expired, training new encodings")
            self.train_all_faces()
    
    def _validate_cache_data(self, encodings, metadata):
        """Validate cache data integrity"""
        if not isinstance(encodings, list) or not isinstance(metadata, list):
            return False
        
        if len(encodings) != len(metadata):
            return False
        
        # Check if cache is too old (max 30 days)
        last_trained = cache.get(self.last_trained_key)
        if last_trained:
            if timezone.now() - last_trained > timedelta(days=30):
                return False
        
        return True
    
    def _build_encoding_cache(self):
        """Build quick lookup cache for encodings"""
        self.encoding_cache = {}
        for idx, metadata in enumerate(self.known_face_metadata):
            person_id = metadata.get('id')
            if person_id:
                self.encoding_cache[person_id] = idx
    
    def train_all_faces(self):
        """Train face encodings for all students and staff with photos"""
        self.known_face_encodings = []
        self.known_face_metadata = []
        
        logger.info(f"Starting face encoding training with model: {self.model_name}")
        
        # Train student faces
        students = Student.objects.filter(
            status='ACTIVE'
        ).select_related('current_class', 'section')
        
        student_count = 0
        for student in students:
            encoding = self._get_face_encoding_for_student(student)
            if encoding is not None:
                self.known_face_encodings.append(encoding)
                self.known_face_metadata.append({
                    'id': str(student.id),
                    'type': 'student',
                    'name': student.full_name,
                    'admission_number': student.admission_number,
                    'class_id': str(student.current_class.id) if student.current_class else None,
                    'section_id': str(student.section.id) if student.section else None,
                    'added_at': timezone.now().isoformat(),
                    'encoding_hash': self._generate_encoding_hash(encoding)
                })
                student_count += 1
        
        # Train staff faces
        staff_members = Staff.objects.filter(
            employment_status='ACTIVE'
        ).select_related('user', 'department')
        
        staff_count = 0
        for staff in staff_members:
            encoding = self._get_face_encoding_for_staff(staff)
            if encoding is not None:
                self.known_face_encodings.append(encoding)
                self.known_face_metadata.append({
                    'id': str(staff.id),
                    'type': 'staff',
                    'name': staff.full_name,
                    'employee_id': staff.employee_id,
                    'department_id': str(staff.department.id) if staff.department else None,
                    'designation': staff.designation.name if staff.designation else None,
                    'added_at': timezone.now().isoformat(),
                    'encoding_hash': self._generate_encoding_hash(encoding)
                })
                staff_count += 1
        
        # Cache encodings and metadata
        if self.known_face_encodings:
            # Convert numpy arrays to lists for JSON serialization
            encodings_list = [enc.tolist() if isinstance(enc, np.ndarray) else enc 
                             for enc in self.known_face_encodings]
            
            cache.set(self.encodings_cache_key, encodings_list, timeout=86400 * 7)  # 7 days
            cache.set(self.metadata_cache_key, self.known_face_metadata, timeout=86400 * 7)
            cache.set(self.last_trained_key, timezone.now(), timeout=None)
            
            self._build_encoding_cache()
            
            logger.info(f"Trained {student_count} student faces and {staff_count} staff faces")
            logger.info(f"Total encodings: {len(self.known_face_encodings)}")
        else:
            logger.warning("No face encodings were generated during training")
    
    def _generate_encoding_hash(self, encoding):
        """Generate hash for encoding for quick comparison"""
        if isinstance(encoding, np.ndarray):
            # Convert to bytes and hash
            return hashlib.md5(encoding.tobytes()).hexdigest()
        return None
    
    def _get_face_encoding_for_student(self, student):
        """Extract face encoding from student's photo using DeepFace"""
        try:
            photo_doc = student.get_photo()
            if not photo_doc or not photo_doc.file:
                logger.debug(f"No photo for student {student.id}")
                return None
            
            # Check if file exists
            if not os.path.exists(photo_doc.file.path):
                logger.warning(f"Photo file not found: {photo_doc.file.path}")
                return None
            
            # Use DeepFace to extract embedding
            try:
                # Preprocess image
                img = functions.preprocess_face(
                    img=photo_doc.file.path,
                    target_size=self.input_shape[:2],
                    enforce_detection=True,
                    detector_backend='opencv',  # or 'mtcnn', 'retinaface', etc.
                    grayscale=False,
                    align=True
                )
                
                # Get embedding
                embedding = self.model.predict(img)[0]
                
                # Normalize if needed (for cosine distance)
                if self.distance_metric == 'cosine':
                    embedding = embedding / np.linalg.norm(embedding)
                
                logger.debug(f"Generated embedding for student {student.id}")
                return embedding
                
            except ValueError as e:
                if "Face could not be detected" in str(e):
                    logger.warning(f"No face detected in student {student.id} photo")
                else:
                    logger.error(f"DeepFace error for student {student.id}: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error encoding face for student {student.id}: {str(e)}")
            return None
    
    def _get_face_encoding_for_staff(self, staff):
        """Extract face encoding from staff's profile photo"""
        try:
            # First check for verified photo usage
            photo_path = None
            
            # Check documents first (preferred)
            photo_doc = staff.documents.filter(document_type='PHOTOGRAPH').first()
            if photo_doc and photo_doc.file:
                photo_path = photo_doc.file.path
            
            # Fallback to profile image
            if not photo_path and staff.profile_image:
                photo_path = staff.profile_image.path
                
            # Check if user has avatar
            if not photo_path and hasattr(staff, 'user') and staff.user and hasattr(staff.user, 'avatar') and staff.user.avatar:
                photo_path = staff.user.avatar.path

            if not photo_path or not os.path.exists(photo_path):
                logger.debug(f"No profile image for staff {staff.id}")
                return None
            
            # Use DeepFace to extract embedding
            try:
                img = functions.preprocess_face(
                    img=photo_path,
                    target_size=self.input_shape[:2],
                    enforce_detection=True,
                    detector_backend='opencv',
                    grayscale=False,
                    align=True
                )
                
                embedding = self.model.predict(img)[0]
                
                if self.distance_metric == 'cosine':
                    embedding = embedding / np.linalg.norm(embedding)
                
                logger.debug(f"Generated embedding for staff {staff.id}")
                return embedding
                
            except ValueError as e:
                if "Face could not be detected" in str(e):
                    logger.warning(f"No face detected in staff {staff.id} photo")
                else:
                    logger.error(f"DeepFace error for staff {staff.id}: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error encoding face for staff {staff.id}: {str(e)}")
            return None
    
    def _process_image(self, image_path, enforce_detection=True):
        """Process image for face detection and alignment"""
        try:
            # Preprocess face
            img = functions.preprocess_face(
                img=image_path,
                target_size=self.input_shape[:2],
                enforce_detection=enforce_detection,
                detector_backend='opencv',
                grayscale=False,
                align=True
            )
            
            # Get embedding
            embedding = self.model.predict(img)[0]
            
            if self.distance_metric == 'cosine':
                embedding = embedding / np.linalg.norm(embedding)
            
            return embedding, True
            
        except ValueError as e:
            if not enforce_detection and "Face could not be detected" in str(e):
                return None, False
            raise e
    
    def recognize_face(self, image_path=None, image_array=None, min_confidence=0.5):
        """
        Recognize a face from an image using DeepFace
        Returns: (metadata, message, confidence, distance)
        """
        try:
            # Process image
            if image_path:
                embedding, detected = self._process_image(image_path, enforce_detection=True)
            elif image_array is not None:
                # Save temporary image for processing
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                cv2.imwrite(temp_file.name, image_array)
                temp_file.close()
                
                try:
                    embedding, detected = self._process_image(temp_file.name, enforce_detection=True)
                finally:
                    os.unlink(temp_file.name)
            else:
                raise ValueError("Either image_path or image_array must be provided")
            
            if not detected or embedding is None:
                return None, "No face detected in image", 0.0, 0.0
            
            # Check if we have any known faces
            if not self.known_face_encodings:
                return None, "No faces trained in the system", 0.0, 0.0
            
            # Find best match
            best_match_idx = -1
            best_distance = float('inf')
            
            for idx, known_encoding in enumerate(self.known_face_encodings):
                # Calculate distance
                if self.distance_metric == 'cosine':
                    distance = dst.findCosineDistance(embedding, known_encoding)
                elif self.distance_metric == 'euclidean':
                    distance = dst.findEuclideanDistance(embedding, known_encoding)
                elif self.distance_metric == 'euclidean_l2':
                    distance = dst.findEuclideanDistance(
                        dst.l2_normalize(embedding),
                        dst.l2_normalize(known_encoding)
                    )
                else:
                    distance = dst.findCosineDistance(embedding, known_encoding)
                
                if distance < best_distance:
                    best_distance = distance
                    best_match_idx = idx
            
            # Convert distance to confidence
            confidence = max(0.0, min(1.0, 1.0 - (best_distance / self.threshold)))
            
            # Check if match meets threshold
            if best_match_idx != -1 and best_distance <= self.threshold and confidence >= min_confidence:
                metadata = self.known_face_metadata[best_match_idx].copy()
                metadata['confidence'] = float(confidence)
                metadata['distance'] = float(best_distance)
                metadata['threshold'] = float(self.threshold)
                
                return metadata, "Face recognized successfully", confidence, best_distance
            else:
                return None, "No matching face found in database", confidence, best_distance
            
        except Exception as e:
            logger.error(f"Face recognition error: {str(e)}", exc_info=True)
            return None, f"Recognition error: {str(e)}", 0.0, 0.0
    
    def recognize_multiple_faces(self, image_path, min_confidence=0.5):
        """Recognize multiple faces in a single image"""
        try:
            # Use DeepFace's built-in multi-face recognition
            results = DeepFace.find(
                img_path=image_path,
                db_path=None,  # We'll handle our own database
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                enforce_detection=True,
                detector_backend='opencv',
                align=True,
                silent=True
            )
            
            # Since we can't pass our custom db, we'll implement custom logic
            # Load image and detect faces
            img = cv2.imread(image_path)
            if img is None:
                return [], "Could not read image"
            
            # Detect faces using OpenCV cascade
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return [], "No faces detected in image"
            
            recognized_faces = []
            
            # Process each face
            for (x, y, w, h) in faces:
                try:
                    # Extract face region
                    face_img = img[y:y+h, x:x+w]
                    
                    # Save temporary face image
                    import tempfile
                    temp_face = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                    cv2.imwrite(temp_face.name, face_img)
                    temp_face.close()
                    
                    # Recognize this face
                    metadata, message, confidence, distance = self.recognize_face(
                        image_path=temp_face.name,
                        min_confidence=min_confidence
                    )
                    
                    # Cleanup
                    os.unlink(temp_face.name)
                    
                    if metadata:
                        metadata['face_location'] = {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}
                        recognized_faces.append(metadata)
                        
                except Exception as e:
                    logger.error(f"Error processing face: {str(e)}")
                    continue
            
            return recognized_faces, f"Found {len(recognized_faces)} recognized faces"
            
        except Exception as e:
            logger.error(f"Multi-face recognition error: {str(e)}")
            return [], f"Recognition error: {str(e)}"
    
    def verify_faces(self, img1_path, img2_path):
        """Verify if two images contain the same person"""
        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                enforce_detection=True,
                detector_backend='opencv',
                align=True,
                normalization='base'
            )
            
            return {
                'verified': result['verified'],
                'distance': float(result['distance']),
                'threshold': float(result['threshold']),
                'model': self.model_name,
                'metric': self.distance_metric
            }
            
        except Exception as e:
            logger.error(f"Face verification error: {str(e)}")
            return {'verified': False, 'error': str(e)}
    
    @transaction.atomic
    def add_new_face(self, person_id, person_type, image_path):
        """Add a new face encoding to the system"""
        try:
            # Verify person exists
            if person_type == 'student':
                person = Student.objects.get(id=person_id)
            elif person_type == 'staff':
                person = Staff.objects.get(id=person_id)
            else:
                raise ValueError(f"Invalid person type: {person_type}")
            
            # Extract encoding
            embedding, detected = self._process_image(image_path, enforce_detection=True)
            
            if not detected or embedding is None:
                return False, "No face found in the provided image"
            
            # Check if person already has encoding
            existing_idx = self.encoding_cache.get(str(person_id))
            
            if existing_idx is not None:
                # Update existing encoding
                self.known_face_encodings[existing_idx] = embedding
                self.known_face_metadata[existing_idx]['encoding_hash'] = self._generate_encoding_hash(embedding)
                self.known_face_metadata[existing_idx]['updated_at'] = timezone.now().isoformat()
                action = "updated"
            else:
                # Add new encoding
                metadata = {
                    'id': str(person_id),
                    'type': person_type,
                    'name': person.full_name,
                    'admission_number': getattr(person, 'admission_number', None),
                    'employee_id': getattr(person, 'employee_id', None),
                    'added_at': timezone.now().isoformat(),
                    'encoding_hash': self._generate_encoding_hash(embedding)
                }
                
                # Add additional fields
                if person_type == 'student':
                    metadata.update({
                        'class_id': str(person.current_class.id) if person.current_class else None,
                        'section_id': str(person.section.id) if person.section else None
                    })
                else:
                    metadata.update({
                        'department_id': str(person.department.id) if person.department else None,
                        'designation': person.designation.name if person.designation else None
                    })
                
                self.known_face_encodings.append(embedding)
                self.known_face_metadata.append(metadata)
                self.encoding_cache[str(person_id)] = len(self.known_face_encodings) - 1
                action = "added"
            
            # Update cache
            self._update_cache()
            
            return True, f"Face {action} successfully"
            
        except Exception as e:
            logger.error(f"Error adding new face: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def _update_cache(self):
        """Update cache with current encodings"""
        # Convert numpy arrays to lists
        encodings_list = [enc.tolist() if isinstance(enc, np.ndarray) else enc 
                         for enc in self.known_face_encodings]
        
        cache.set(self.encodings_cache_key, encodings_list, timeout=86400 * 7)
        cache.set(self.metadata_cache_key, self.known_face_metadata, timeout=86400 * 7)
        cache.set(self.last_trained_key, timezone.now(), timeout=None)
    
    def retrain_model(self, model_name=None, metric=None):
        """Retrain model with optional new configuration"""
        try:
            # Update configuration if provided
            if model_name and model_name in self.AVAILABLE_MODELS:
                self.model_name = model_name
                self.model = DeepFace.build_model(model_name)
                self.input_shape = functions.find_input_shape(self.model)
            
            if metric and metric in self.AVAILABLE_METRICS:
                self.distance_metric = metric
            
            # Update cache keys
            self.encodings_cache_key = f'deepface_encodings_{self.model_name}'
            self.metadata_cache_key = f'deepface_metadata_{self.model_name}'
            
            # Clear old cache
            cache.delete(f'deepface_encodings_*')
            cache.delete(f'deepface_metadata_*')
            
            # Retrain
            self.train_all_faces()
            
            return True, f"Model retrained with {len(self.known_face_encodings)} encodings"
            
        except Exception as e:
            logger.error(f"Retraining error: {str(e)}")
            return False, f"Retraining failed: {str(e)}"
    
    def get_stats(self):
        """Get statistics about the face recognition system"""
        stats = {
            'system_status': 'active',
            'model': self.get_model_info(),
            'total_encodings': len(self.known_face_encodings),
            'student_encodings': len([m for m in self.known_face_metadata if m['type'] == 'student']),
            'staff_encodings': len([m for m in self.known_face_metadata if m['type'] == 'staff']),
            'cache_timestamp': cache.get(self.last_trained_key),
            'cache_size_mb': self._estimate_cache_size(),
            'threshold': self.threshold,
            'encoding_dimension': self.known_face_encodings[0].shape[0] if self.known_face_encodings else 0
        }
        
        return stats
    
    def _estimate_cache_size(self):
        """Estimate cache size in MB"""
        try:
            import sys
            total_size = 0
            
            # Estimate size of encodings
            for enc in self.known_face_encodings:
                total_size += enc.nbytes if isinstance(enc, np.ndarray) else sys.getsizeof(enc)
            
            # Estimate size of metadata
            import json
            metadata_json = json.dumps(self.known_face_metadata)
            total_size += sys.getsizeof(metadata_json)
            
            return round(total_size / (1024 * 1024), 2)  # Convert to MB
            
        except Exception:
            return 0.0
    
    def health_check(self):
        """Perform health check on the service"""
        health = {
            'status': 'healthy',
            'model_loaded': self.model is not None,
            'encodings_loaded': len(self.known_face_encodings) > 0,
            'cache_valid': bool(cache.get(self.encodings_cache_key)),
            'timestamp': timezone.now().isoformat()
        }
        
        # Test with a sample if available
        if self.known_face_encodings:
            try:
                # Create a dummy test
                test_embedding = np.random.randn(*self.known_face_encodings[0].shape)
                test_embedding = test_embedding / np.linalg.norm(test_embedding)
                
                health['test_embedding_generated'] = True
                health['embedding_dimension'] = test_embedding.shape[0]
            except Exception as e:
                health['test_embedding_generated'] = False
                health['test_error'] = str(e)
        
        return health


# Global singleton instance
deepface_service = DeepFaceRecognitionService()