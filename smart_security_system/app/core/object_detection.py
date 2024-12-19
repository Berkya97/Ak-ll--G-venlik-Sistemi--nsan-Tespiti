import cv2
import numpy as np
from collections import deque
import time

class YOLODetector:
    def __init__(self, config_path, weights_path, names_path):
        self.net = cv2.dnn.readNet(weights_path, config_path)
        
        # CUDA kullanımını etkinleştir
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        
        with open(names_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
            
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        self.colors = {
            'person': (0, 0, 255),
            'authorized': (0, 255, 0),
            'other': (0, 255, 0)
        }
        
        # Performans parametreleri
        self.input_size = (416, 416)
        self.scale = 1/255.0
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.3
        self.frame_skip = 1  # Her frame'i işle
        self.frame_count = 0
        
        # Tespit kararlılığı için
        self.detection_history = deque(maxlen=3)  # Son 3 tespit
        self.last_detection_time = time.time()
        self.detection_timeout = 0.1  # 100ms
        self.last_valid_detections = None
        
    def smooth_detections(self, current_detections):
        """Tespitleri yumuşat"""
        if not current_detections[0]:  # Boş tespit listesi
            if time.time() - self.last_detection_time < self.detection_timeout:
                return self.last_valid_detections
            return current_detections
            
        self.detection_history.append(current_detections)
        self.last_detection_time = time.time()
        self.last_valid_detections = current_detections
        
        return current_detections
        
    def detect_objects(self, frame):
        self.frame_count += 1
        
        # Frame'i küçült
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            frame = cv2.resize(frame, None, fx=scale, fy=scale)
        
        try:
            blob = cv2.dnn.blobFromImage(
                frame, 
                self.scale, 
                self.input_size, 
                swapRB=True, 
                crop=False
            )
            self.net.setInput(blob)
            
            outs = self.net.forward(self.output_layers)
            
            boxes = []
            confidences = []
            class_ids = []
            
            # Tespitleri işle
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > self.confidence_threshold:
                        center_x = int(detection[0] * frame.shape[1])
                        center_y = int(detection[1] * frame.shape[0])
                        w = int(detection[2] * frame.shape[1])
                        h = int(detection[3] * frame.shape[0])
                        
                        x = int(center_x - w/2)
                        y = int(center_y - h/2)
                        
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            
            # Non-maximum suppression uygula
            if boxes:
                indexes = cv2.dnn.NMSBoxes(
                    boxes, 
                    confidences, 
                    self.confidence_threshold, 
                    self.nms_threshold
                )
                
                final_boxes = []
                final_confidences = []
                final_class_ids = []
                
                if len(indexes) > 0:
                    indexes = indexes.flatten()
                    for i in indexes:
                        final_boxes.append(boxes[i])
                        final_confidences.append(confidences[i])
                        final_class_ids.append(class_ids[i])
                
                result = (final_boxes, final_confidences, final_class_ids)
            else:
                result = ([], [], [])
            
            # Tespitleri yumuşat
            smoothed_result = self.smooth_detections(result)
            return smoothed_result
            
        except cv2.error as e:
            print(f"OpenCV Hatası: {e}")
            return [], [], []
        except Exception as e:
            print(f"Hata: {e}")
            return [], [], []

    def draw_detections(self, frame, boxes, confidences, class_ids, is_authorized=False):
        # Orijinal frame'i koru
        output_frame = frame.copy()
        
        # Frame'i küçült
        height, width = output_frame.shape[:2]
        if width > 640:
            scale = 640 / width
            output_frame = cv2.resize(output_frame, None, fx=scale, fy=scale)
        
        for i in range(len(boxes)):
            x, y, w, h = boxes[i]
            label = str(self.classes[class_ids[i]])
            confidence = confidences[i]
            
            if label == 'person':
                color = self.colors['authorized'] if is_authorized else self.colors['person']
                
                # Çerçeveyi çiz
                cv2.rectangle(output_frame, (x, y), (x + w, y + h), color, 2)
                
                # Etiket metni
                label_text = f"{label} ({confidence:.2f})"
                cv2.putText(output_frame, label_text, (x, y - 5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return output_frame
