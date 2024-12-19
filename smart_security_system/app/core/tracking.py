import cv2

class PersonTracker:
    def __init__(self):
        self.trackers = []
        self.tracker_types = ['CSRT', 'KCF', 'MOSSE']
        self.current_tracker = 'CSRT'
        
    def create_tracker(self):
        if self.current_tracker == 'CSRT':
            return cv2.TrackerCSRT_create()
        elif self.current_tracker == 'KCF':
            return cv2.TrackerKCF_create()
        elif self.current_tracker == 'MOSSE':
            return cv2.TrackerMOSSE_create()
            
    def start_tracking(self, frame, bbox):
        tracker = self.create_tracker()
        success = tracker.init(frame, bbox)
        if success:
            self.trackers.append(tracker)
            
    def update_all(self, frame):
        tracked_objects = []
        for tracker in self.trackers:
            success, bbox = tracker.update(frame)
            if success:
                tracked_objects.append(bbox)
        return tracked_objects
