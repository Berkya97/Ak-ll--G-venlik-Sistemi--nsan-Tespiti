import face_recognition
import cv2
import os
import cupy as cp

class FaceDetector:
    def __init__(self, authorized_images_path):
        self.authorized_encodings = []
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.authorized_images_path = os.path.join(base_dir, 'data', 'authorized_faces')
        
        if not os.path.exists(self.authorized_images_path):
            raise FileNotFoundError(f"Hata: '{self.authorized_images_path}' klasörü bulunamadı.")
            
        self.load_authorized_faces(self.authorized_images_path)
        print(f"GPU Hazır: {cp.cuda.runtime.getDeviceCount()} adet GPU bulundu")
        print(f"CUDA Sürümü: {cp.cuda.runtime.runtimeGetVersion()}")
    
    def load_authorized_faces(self, authorized_images_path):
        for filename in os.listdir(authorized_images_path):
            if filename.endswith((".jpg", ".png")):
                image_path = os.path.join(authorized_images_path, filename)
                try:
                    image = face_recognition.load_image_file(image_path)
                    # GPU'ya transfer
                    gpu_image = cp.asarray(image)
                    # CPU'ya geri transfer ve yüz kodlama
                    encoding = face_recognition.face_encodings(cp.asnumpy(gpu_image))[0]
                    self.authorized_encodings.append(encoding)
                    print(f"{filename} dosyasından yüz kodlaması alındı (GPU ile)")
                except Exception as e:
                    print(f"Hata: '{filename}' dosyası yüklenemedi. Hata: {e}")
    
    def detect_faces(self, frame):
        try:
            # Frame'i GPU'ya transfer et
            gpu_frame = cp.asarray(frame)
            
            # RGB'ye dönüştür
            rgb_frame = cv2.cvtColor(cp.asnumpy(gpu_frame), cv2.COLOR_BGR2RGB)
            
            # Yüz tespiti
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            person_detected = False
            is_authorized_person = False
            
            for face_encoding in face_encodings:
                # GPU'da karşılaştırma
                matches = face_recognition.compare_faces(
                    self.authorized_encodings, 
                    face_encoding, 
                    tolerance=0.6
                )
                if True in matches:
                    is_authorized_person = True
                    break
                else:
                    person_detected = True
                    
            return person_detected, is_authorized_person
            
        except Exception as e:
            print(f"GPU işlem hatası: {e}")
            # CPU'ya geri dön
            return self._detect_faces_cpu(frame)
    
    def _detect_faces_cpu(self, frame):
        # Yedek CPU-based tespit
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        person_detected = False
        is_authorized_person = False
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                self.authorized_encodings, 
                face_encoding, 
                tolerance=0.6
            )
            if True in matches:
                is_authorized_person = True
                break
            else:
                person_detected = True
                
        return person_detected, is_authorized_person
