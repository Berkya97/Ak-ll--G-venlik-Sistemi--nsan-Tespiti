from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from ..core.face_detection import FaceDetector
from ..utils.database import SecurityDatabase

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class SecurityStatus(Resource):
    def __init__(self):
        self.db = SecurityDatabase()
        
    def get(self):
        # Sistem durumunu getir
        return jsonify({
            'camera_status': 'active',
            'last_detection': self.db.get_last_detection(),
            'alarm_status': 'inactive',
            'authorized_count': self.db.get_authorized_count(),
            'unauthorized_count': self.db.get_unauthorized_count()
        })

class DetectionEvents(Resource):
    def __init__(self):
        self.db = SecurityDatabase()
        
    def get(self):
        # Son tespitleri getir
        events = self.db.get_recent_events(limit=10)
        return jsonify(events)
        
    def post(self):
        # Yeni tespit olayı kaydet
        data = request.get_json()
        self.db.log_event(
            event_type=data['event_type'],
            person_detected=data['person_detected'],
            authorized=data['authorized']
        )
        return {'status': 'success'}, 201

api.add_resource(SecurityStatus, '/api/status')
api.add_resource(DetectionEvents, '/api/events')
