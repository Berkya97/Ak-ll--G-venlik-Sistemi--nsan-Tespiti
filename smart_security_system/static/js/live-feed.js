class LiveFeed {
    constructor() {
        this.stream = document.getElementById('live-stream');
        this.detectionList = document.getElementById('detection-list');
        this.isRecording = false;
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.stream.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    takeSnapshot() {
        const canvas = document.createElement('canvas');
        canvas.width = this.stream.videoWidth;
        canvas.height = this.stream.videoHeight;
        canvas.getContext('2d').drawImage(this.stream, 0, 0);
        
        const link = document.createElement('a');
        link.download = `snapshot-${Date.now()}.png`;
        link.href = canvas.toDataURL();
        link.click();
    }

    updateDetectionList(detections) {
        this.detectionList.innerHTML = '';
        detections.forEach(detection => {
            const li = document.createElement('li');
            li.textContent = `${detection.label} (${Math.round(detection.confidence * 100)}%)`;
            this.detectionList.appendChild(li);
        });
    }
}

const liveFeed = new LiveFeed();
