import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

class SecuritySystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AkılGöz Güvenlik Sistemi")
        self.root.geometry("1200x800")
        
        # Ana frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Sol panel - Kamera görüntüsü
        self.camera_frame = ttk.LabelFrame(self.main_frame, text="Canlı Kamera")
        self.camera_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack(expand=True, fill='both')
        
        # Sağ panel - Kontroller ve İstatistikler
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Kontrol Paneli")
        self.control_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Kontrol butonları
        self.start_button = ttk.Button(self.control_frame, text="Kamerayı Başlat")
        self.start_button.pack(pady=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Kamerayı Durdur")
        self.stop_button.pack(pady=5)
        
        # İstatistik paneli
        self.stats_frame = ttk.LabelFrame(self.control_frame, text="İstatistikler")
        self.stats_frame.pack(fill='x', pady=10, padx=5)
        
        # İstatistik değişkenleri
        self.detected_count = tk.StringVar(value="Tespit: 0")
        self.authorized_count = tk.StringVar(value="Yetkili: 0")
        self.unauthorized_count = tk.StringVar(value="Yetkisiz: 0")
        
        # İstatistik etiketleri
        ttk.Label(self.stats_frame, textvariable=self.detected_count).pack(pady=2)
        ttk.Label(self.stats_frame, textvariable=self.authorized_count).pack(pady=2)
        ttk.Label(self.stats_frame, textvariable=self.unauthorized_count).pack(pady=2)
        
        # Alarm kontrol paneli
        self.alarm_frame = ttk.LabelFrame(self.control_frame, text="Alarm Kontrolü")
        self.alarm_frame.pack(fill='x', pady=10, padx=5)
        
        # Alarm ses seviyesi kontrolü
        self.volume_scale = ttk.Scale(self.alarm_frame, from_=0, to=100, orient='horizontal')
        self.volume_scale.set(50)
        self.volume_scale.pack(fill='x', padx=5, pady=5)
        
        # Test butonu
        self.test_alarm_button = ttk.Button(self.alarm_frame, text="Alarmı Test Et")
        self.test_alarm_button.pack(pady=5)
        
        # Grid ağırlıklarını ayarla
        self.main_frame.grid_columnconfigure(0, weight=3)  # Kamera frame'i daha geniş
        self.main_frame.grid_columnconfigure(1, weight=1)  # Kontrol frame'i daha dar
        
    def update_camera(self, frame):
        """Kamera görüntüsünü güncelle"""
        if frame is not None:
            # OpenCV BGR formatından RGB'ye dönüştür
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # PIL Image'a dönüştür
            image = Image.fromarray(frame_rgb)
            # Frame boyutlarını ayarla
            image = image.resize((800, 600), Image.Resampling.LANCZOS)
            # PhotoImage'a dönüştür
            photo = ImageTk.PhotoImage(image=image)
            # Label'ı güncelle
            self.camera_label.configure(image=photo)
            self.camera_label.image = photo
            
    def update_stats(self, detected=0, authorized=0, unauthorized=0):
        """İstatistikleri güncelle"""
        self.detected_count.set(f"Tespit: {detected}")
        self.authorized_count.set(f"Yetkili: {authorized}")
        self.unauthorized_count.set(f"Yetkisiz: {unauthorized}")
        
    def set_start_callback(self, callback):
        """Kamera başlatma butonu için callback fonksiyonu"""
        self.start_button.configure(command=callback)
        
    def set_stop_callback(self, callback):
        """Kamera durdurma butonu için callback fonksiyonu"""
        self.stop_button.configure(command=callback)
        
    def set_test_alarm_callback(self, callback):
        """Alarm test butonu için callback fonksiyonu"""
        self.test_alarm_button.configure(command=callback)
