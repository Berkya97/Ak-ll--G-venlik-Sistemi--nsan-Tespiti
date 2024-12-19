import pygame
import os
import threading
import time

class AlertSystem:
    def __init__(self, alarm_sound_path="data/alarm/alarm.mp3"):
        pygame.mixer.init()
        self.alarm_sound_path = self._get_alarm_path(alarm_sound_path)
        
        # Durum değişkenleri
        self.is_alarm_active = False
        self.alarm_thread = None
        self.authorized_present = False
        self.unauthorized_present = False  # Yetkisiz kişi durumu eklendi
        
    def _get_alarm_path(self, alarm_sound_path):
        if not os.path.isabs(alarm_sound_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(base_dir, alarm_sound_path)
        return alarm_sound_path
    
    def update_detection_status(self, authorized_detected, unauthorized_detected):
        """Tespit durumlarını güncelle"""
        self.authorized_present = authorized_detected
        self.unauthorized_present = unauthorized_detected
        
        # Alarm durumunu güncelle
        if self.authorized_present:
            # Yetkili kişi varsa alarmı durdur
            self.stop_alarm()
        elif self.unauthorized_present and not self.is_alarm_active:
            # Yetkili yoksa ve yetkisiz varsa alarmı başlat
            self.trigger_alarm()
        elif not self.unauthorized_present:
            # Yetkisiz kişi yoksa alarmı durdur
            self.stop_alarm()
    
    def trigger_alarm(self):
        """Alarmı tetikle"""
        if not self.authorized_present and not self.is_alarm_active:
            self.is_alarm_active = True
            self.alarm_thread = threading.Thread(target=self._play_alarm)
            self.alarm_thread.daemon = True
            self.alarm_thread.start()
    
    def stop_alarm(self):
        """Alarmı durdur"""
        self.is_alarm_active = False
        pygame.mixer.music.stop()
    
    def _play_alarm(self):
        """Alarm sesini çal"""
        while self.is_alarm_active:
            if not self.authorized_present and self.unauthorized_present:
                pygame.mixer.music.load(self.alarm_sound_path)
                pygame.mixer.music.play(-1)
                while (pygame.mixer.music.get_busy() and 
                       self.is_alarm_active and 
                       not self.authorized_present and 
                       self.unauthorized_present):
                    time.sleep(0.1)
                pygame.mixer.music.stop()
            else:
                self.stop_alarm()
                break
    
    def set_volume(self, volume):
        """Alarm ses seviyesini ayarla (0-100)"""
        pygame.mixer.music.set_volume(volume / 100.0)
    
    def test_alarm(self):
        """Alarm testini çalıştır"""
        temp_auth = self.authorized_present
        temp_unauth = self.unauthorized_present
        
        self.authorized_present = False
        self.unauthorized_present = True
        
        pygame.mixer.music.load(self.alarm_sound_path)
        pygame.mixer.music.play()
        time.sleep(2)
        pygame.mixer.music.stop()
        
        self.authorized_present = temp_auth
        self.unauthorized_present = temp_unauth
