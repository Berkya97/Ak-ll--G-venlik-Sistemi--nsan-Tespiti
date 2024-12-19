import cv2
import numpy as np

class MotionDetector:
    def __init__(self):
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.min_area = 500
        
    def detect_motion(self, frame):
        # Arka plan çıkarma
        fg_mask = self.background_subtractor.apply(frame)
        
        # Gürültü temizleme
        kernel = np.ones((3,3), np.uint8)
        fg_mask = cv2.erode(fg_mask, kernel, iterations=1)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)
        
        # Hareket eden nesneleri tespit et
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                motion_detected = True
                break
                
        return motion_detected, fg_mask
