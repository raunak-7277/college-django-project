class RoomMediaController {
    constructor(options) {
        this.localVideo = options.localVideo;
        this.remoteVideo = options.remoteVideo;
        this.statusElement = options.statusElement;
        this.localStream = null;
    }

    async initialize() {
        if (!this.localVideo) return;

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.setStatus('Camera preview is not supported in this browser.');
            return;
        }

        this.setStatus('Requesting camera & microphone access...');

        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true   // ✅ FIXED
            });

            this.attachLocalStream(this.localStream);
            this.setStatus('Local preview is live.');

        } catch (error) {
            console.error('Media access error:', error);
            this.setStatus('Camera/Mic access denied.');
        }
    }

    attachLocalStream(stream) {
        if (this.localVideo) {
            this.localVideo.srcObject = stream;
        }
    }

    setRemoteStream(stream) {
        if (this.remoteVideo) {
            this.remoteVideo.srcObject = stream;
        }
    }

    stopLocalStream() {
        if (!this.localStream) return;

        this.localStream.getTracks().forEach(track => track.stop());
        this.localStream = null;

        if (this.localVideo) {
            this.localVideo.srcObject = null;
        }

        this.setStatus('Local stream stopped.');
    }

    setStatus(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const localVideo = document.getElementById('localVideo');

    if (!localVideo) return;

    const controller = new RoomMediaController({
        localVideo,
        remoteVideo: document.getElementById('remoteVideo'),
        statusElement: document.getElementById('mediaStatus'),
    });

    controller.initialize();
    
    window.addEventListener('beforeunload', () => {
        controller.stopLocalStream();
    });

    window.roomMediaController = controller;
});