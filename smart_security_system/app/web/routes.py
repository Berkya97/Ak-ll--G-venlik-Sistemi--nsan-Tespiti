from flask import Blueprint, render_template, Response
from flask_socketio import emit
from . import socketio
import cv2
import json

# Blueprint oluştur
main = Blueprint('main', __name__)

# Global değişkenler
frame_buffer = None
stats = {
    'detected': 0,
    'authorized': 0,
    'unauthorized': 0,
    'alarm_active': False
}

@main.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@main.route('/video_feed')
def video_feed():
    """Video akışı"""
    def generate_frames():
        while True:
            if frame_buffer is not None:
                # Frame'i JPEG formatına dönüştür
                ret, buffer = cv2.imencode('.jpg', frame_buffer)
                if ret:
                    # Byte dizisine çevir
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def update_frame(frame):
    """Kamera görüntüsünü güncelle"""
    global frame_buffer
    frame_buffer = frame

def update_stats(detected, authorized, unauthorized, alarm_active=False):
    """İstatistikleri güncelle ve WebSocket ile gönder"""
    global stats
    stats = {
        'detected': detected,
        'authorized': authorized,
        'unauthorized': unauthorized,
        'alarm_active': alarm_active
    }
    
    # WebSocket ile istatistikleri gönder
    socketio.emit('stats_update', json.dumps(stats))

@main.route('/api/stats')
def get_stats():
    """İstatistikleri JSON olarak döndür"""
    return json.dumps(stats)

# WebSocket olayları
@socketio.on('connect')
def handle_connect():
    """Client bağlandığında"""
    emit('stats_update', json.dumps(stats))

@socketio.on('disconnect')
def handle_disconnect():
    """Client bağlantısı kesildiğinde"""
    pass
