class RoomMediaController {
    constructor(options) {
        this.localVideo = options.localVideo;
        this.remoteVideo = options.remoteVideo;
        this.statusElement = options.statusElement;
        this.localStream = null;
    }

    async initialize() {
        if (!this.localVideo) {
            return;
        }

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.setStatus('Camera preview is not supported in this browser.');
            return;
        }

        this.setStatus('Requesting access to your camera...');

        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false,
            });

            this.attachLocalStream(this.localStream);
            this.setStatus('Local camera preview is live.');
        } catch (error) {
            console.error('Unable to start local camera preview.', error);
            this.setStatus('Camera access was denied or is unavailable.');
        }
    }

    attachLocalStream(stream) {
        this.localVideo.srcObject = stream;
    }

    setRemoteStream(stream) {
        if (this.remoteVideo) {
            this.remoteVideo.srcObject = stream;
        }
    }

    stopLocalStream() {
        if (!this.localStream) {
            return;
        }

        this.localStream.getTracks().forEach((track) => track.stop());
        this.localStream = null;
        this.localVideo.srcObject = null;
        this.setStatus('Local camera preview stopped.');
    }

    setStatus(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const localVideo = document.getElementById('localVideo');

    if (!localVideo) {
        return;
    }

    const roomMediaController = new RoomMediaController({
        localVideo,
        remoteVideo: document.getElementById('remoteVideo'),
        statusElement: document.getElementById('mediaStatus'),
    });

    roomMediaController.initialize();
    window.roomMediaController = roomMediaController;
});
