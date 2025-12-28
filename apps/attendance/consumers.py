import json
import base64
import numpy as np
import cv2
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.attendance.services.face_recognition_service import face_service
from apps.students.models import Student
from apps.hr.models import Staff
import asyncio
import logging

logger = logging.getLogger(__name__)

class FaceRecognitionConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time face recognition"""
    
    async def connect(self):
        await self.accept()
        self.recognition_active = False
        self.camera_id = None
    
    async def disconnect(self, close_code):
        self.recognition_active = False
    
    async def receive(self, text_data):
        """Receive messages from WebSocket client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'start_recognition':
                self.recognition_active = True
                self.camera_id = data.get('camera_id')
                att_type = data.get('attendance_type', 'student')
                await self.send(json.dumps({
                    'type': 'status',
                    'message': 'Face recognition started',
                    'camera_id': self.camera_id
                }))
                
            elif message_type == 'stop_recognition':
                self.recognition_active = False
                await self.send(json.dumps({
                    'type': 'status',
                    'message': 'Face recognition stopped'
                }))
                
            elif message_type == 'frame' and self.recognition_active:
                # Process frame from client
                frame_data = data.get('frame')
                await self.process_frame(frame_data, data.get('attendance_type', 'student'))
                
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            await self.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def process_frame(self, frame_data, att_type):
        """Process a single frame for face recognition"""
        try:
            # Decode base64 frame
            if 'base64,' in frame_data:
                frame_data = frame_data.split('base64,')[1]
            
            image_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return
            
            # Convert to RGB (face_recognition uses RGB)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            if face_locations:
                # Get face encodings
                face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
                
                recognition_results = []
                
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    # Compare with known faces
                    matches = face_recognition.compare_faces(
                        face_service.known_face_encodings,
                        face_encoding,
                        tolerance=face_service.tolerance
                    )
                    
                    if True in matches:
                        first_match_index = matches.index(True)
                        metadata = face_service.known_face_metadata[first_match_index]
                        
                        recognition_results.append({
                            'type': metadata['type'],
                            'name': metadata['name'],
                            'id': metadata['id'],
                            'location': face_location,
                            'attendance_type': att_type
                        })
                
                # Send recognition results
                if recognition_results:
                    await self.send(json.dumps({
                        'type': 'recognition_result',
                        'results': recognition_results,
                        'timestamp': asyncio.get_event_loop().time()
                    }))
            
            # Draw rectangles on faces (for visualization)
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Convert back to base64 for sending
            _, buffer = cv2.imencode('.jpg', image)
            processed_frame = base64.b64encode(buffer).decode('utf-8')
            
            await self.send(json.dumps({
                'type': 'processed_frame',
                'frame': f"data:image/jpeg;base64,{processed_frame}",
                'face_count': len(face_locations)
            }))
            
        except Exception as e:
            logger.error(f"Frame processing error: {str(e)}")