class SecurityAlerts {
    constructor() {
        this.alarmSound = new Audio('/static/sounds/alarm.mp3');
    }

    showAlert(message, type = 'warning') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    playAlarm() {
        this.alarmSound.loop = true;
        this.alarmSound.play();
    }

    stopAlarm() {
        this.alarmSound.pause();
        this.alarmSound.currentTime = 0;
    }
}

const securityAlerts = new SecurityAlerts();
