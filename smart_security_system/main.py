import tkinter as tk
from app.gui.main_window import SecuritySystemGUI
from app.web import create_app
from app.core.face_detection import FaceDetector
from app.core.object_detection import YOLODetector
from app.utils.notifications import AlertSystem
from app.utils.database import SecurityDatabase
import threading
import yaml
import logging
import cv2
import time
import numpy as np
import torch
import os
import face_recognition

#yetkili yüzleri authorized_faces klasöründe tutacağız

class SecuritySystem:
    def __init__(self):
        # Konfigürasyon yükleme
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Logger kurulumu
        self.logger = self.setup_logger()
        
        # Veritabanı başlatma
        self.db = SecurityDatabase()
        
        # Tespit sistemleri
        self.face_detector = FaceDetector("data/authorized_faces")
        self.yolo_detector = YOLODetector(
            "models/yolo/yolov3.cfg",
            "models/yolo/yolov3.weights",
            "models/yolo/coco.names"
        )
        
        # Alarm sistemi
        self.alert_system = AlertSystem()
        
        # Kamera değişkenleri
        self.cap = None
        self.is_running = False
        self.camera_thread = None
        
        # GUI başlatma
        self.root = tk.Tk()
        self.gui = SecuritySystemGUI(self.root)
        
        # GUI callback'lerini ayarla
        self.gui.set_start_callback(self.start_camera)
        self.gui.set_stop_callback(self.stop_camera)
        self.gui.set_test_alarm_callback(self.test_alarm)
        
        # Web sunucusu başlatma
        self.web_app = create_app()
        
        # YOLO modelini yükle
        self.net = cv2.dnn.readNet(
            "models/yolo/yolov3.weights",
            "models/yolo/yolov3.cfg"
        )
        
        # COCO sınıf isimlerini yükle
        with open("models/yolo/coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        self.use_cuda = False
        try:
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                self.use_cuda = True
                self.stream = cv2.cuda.Stream()
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                print("GPU modu aktif")
            else:
                print("GPU bulunamadı, CPU modu kullanılacak")
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        except Exception as e:
            print(f"CUDA desteği yok, CPU modu kullanılacak: {str(e)}")
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
        # Kamera ayarları
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Diğer başlangıç ayarları
        self.known_face_encodings = []
        self.known_face_names = []
        self.camera = cv2.VideoCapture(0)
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        
        # Bilinen yüzleri yükle
        self.load_known_faces()
        
    def setup_logger(self):
        logger = logging.getLogger('SecuritySystem')
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler('logs/security.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def start_camera(self):
        """Kamerayı başlat"""
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.logger.error("Kamera açılamadı!")
                return
                
            self.is_running = True
            self.camera_thread = threading.Thread(target=self.camera_loop)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            self.logger.info("Kamera başlatıldı")
    
    def stop_camera(self):
        """Kamerayı durdur"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.logger.info("Kamera durduruldu")
    
    def camera_loop(self):
        """Kamera döngüsü"""
        detected_count = 0
        authorized_count = 0
        unauthorized_count = 0
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            try:
                # Frame'i GPU'ya taşı
                if self.use_cuda:
                    gpu_frame = cv2.cuda_GpuMat()
                    gpu_frame.upload(frame, self.stream)
                    
                    # GPU üzerinde ön işleme
                    gpu_frame = cv2.cuda.resize(gpu_frame, (640, 480), stream=self.stream)
                    gpu_frame = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2RGB, stream=self.stream)
                    
                    # Stream'i bekle
                    self.stream.waitForCompletion()
                    
                    # İşlenmiş frame'i CPU'ya geri al
                    frame = gpu_frame.download()
                
                # Yüz tespiti
                person_detected, is_authorized = self.face_detector.detect_faces(frame)
                
                # YOLO ile nesne tespiti
                boxes, confidences, class_ids = self.yolo_detector.detect_objects(frame)
                
                # Tespitleri çiz
                frame = self.yolo_detector.draw_detections(frame, boxes, confidences, class_ids, is_authorized)
                
                # Tespit durumlarını belirle
                unauthorized_detected = person_detected and not is_authorized
                
                # Alarm sistemini güncelle
                self.alert_system.update_detection_status(is_authorized, unauthorized_detected)
                
                # İstatistikleri güncelle
                if person_detected:
                    detected_count += 1
                    if is_authorized:
                        authorized_count += 1
                    else:
                        unauthorized_count += 1
                
                # Web arayüzünü güncelle
                from app.web.routes import update_frame, update_stats
                update_frame(frame)
                update_stats(
                    detected_count,
                    authorized_count,
                    unauthorized_count,
                    self.alert_system.is_alarm_active
                )
                
                # GUI'yi güncelle
                self.gui.update_camera(frame)
                self.gui.update_stats(detected_count, authorized_count, unauthorized_count)
                
            except Exception as e:
                self.logger.error(f"Kamera döngüsünde hata: {e}")
                
            # FPS kontrolü
            time.sleep(1/60)
    
    def test_alarm(self):
        """Alarmı test et"""
        self.alert_system.trigger_alarm()
        self.logger.info("Alarm testi yapıldı")
        
    def start_web_server(self):
        """Web sunucusunu ayrı bir thread'de başlat"""
        self.web_app.run(
            host=self.config['web']['host'],
            port=self.config['web']['port'],
            debug=self.config['web']['debug']
        )
        
    def run(self):
        """Ana uygulamayı başlat"""
        # Web sunucusunu ayrı thread'de başlat
        web_thread = threading.Thread(target=self.start_web_server)
        web_thread.daemon = True
        web_thread.start()
        
        # GUI'yi başlat
        self.root.mainloop()
    
    def __del__(self):
        """Temizlik işlemleri"""
        self.cap.release()
        if hasattr(self, 'stream') and self.use_cuda:
            self.stream.free()
    
    def load_known_faces(self):
        """Bilinen yüzleri yükler ve kodlar"""
        known_faces_dir = "data/authorized_faces"  # Bilinen yüzlerin bulunduğu klasör
        
        # Klasör yoksa uyarı ver
        if not os.path.exists(known_faces_dir):
            print(f"Hata: '{known_faces_dir}' klasörü bulunamadı!")
            return

        # Klasördeki her resmi işle
        for filename in os.listdir(known_faces_dir):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(known_faces_dir, filename)
                try:
                    # Resmi yükle ve yüz kodlamasını al
                    image = face_recognition.load_image_file(image_path)
                    encoding = face_recognition.face_encodings(image)[0]
                    
                    # İsmi dosya adından al (uzantıyı çıkar)
                    name = os.path.splitext(filename)[0]
                    
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(name)
                    
                    print(f"{filename} dosyasından yüz kodlaması alındı {'(GPU ile)' if self.use_cuda else '(CPU ile)'}")
                except Exception as e:
                    print(f"Hata: {filename} dosyası işlenemedi - {str(e)}")

if __name__ == "__main__":
    security_system = SecuritySystem()
    security_system.run()
