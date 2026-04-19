class RoomMediaController {
    constructor(options) {
        this.localVideo = options.localVideo;
        this.remoteVideo = options.remoteVideo;
        this.statusElement = options.statusElement;
        this.micButton = options.micButton;
        this.cameraButton = options.cameraButton;
        this.micStateElement = options.micStateElement;
        this.cameraStateElement = options.cameraStateElement;

        this.localStream = null;
        this.peerConnection = null;
        this.socket = null;

        this.roomId = window.roomConfig?.roomId || window.location.pathname.split("/")[2];

        this.hasCreatedOffer = false;
    }

    async initialize() {
        try {
            this.setStatus("Requesting camera...");

            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            this.localVideo.srcObject = this.localStream;

            this.createPeerConnection();
            this.addLocalTracks();
            this.connectWebSocket();
            this.updateControlStates();
            this.setStatus("Ready");

        } catch (err) {
            console.error("Media error:", err);
            this.updateControlStates(false);
            this.setStatus("Camera/Mic access failed");
        }
    }

    updateControlStates(isReady = true) {
        if (this.micButton) {
            this.micButton.disabled = !isReady;
        }

        if (this.cameraButton) {
            this.cameraButton.disabled = !isReady;
        }

        if (!this.localStream) return;

        const audioTrack = this.localStream.getAudioTracks()[0];
        const videoTrack = this.localStream.getVideoTracks()[0];

        if (this.micButton && audioTrack) {
            this.micButton.textContent = audioTrack.enabled ? "Mic ON" : "Mic OFF";
            this.micButton.classList.toggle("btn-primary", audioTrack.enabled);
            this.micButton.classList.toggle("btn-danger", !audioTrack.enabled);
        }

        if (this.micStateElement && audioTrack) {
            this.micStateElement.textContent = audioTrack.enabled ? "ON" : "OFF";
            this.micStateElement.classList.toggle("text-bg-success", audioTrack.enabled);
            this.micStateElement.classList.toggle("text-bg-danger", !audioTrack.enabled);
        }

        if (this.cameraButton && videoTrack) {
            this.cameraButton.textContent = videoTrack.enabled ? "Camera ON" : "Camera OFF";
            this.cameraButton.classList.toggle("btn-secondary", videoTrack.enabled);
            this.cameraButton.classList.toggle("btn-danger", !videoTrack.enabled);
        }

        if (this.cameraStateElement && videoTrack) {
            this.cameraStateElement.textContent = videoTrack.enabled ? "ON" : "OFF";
            this.cameraStateElement.classList.toggle("text-bg-success", videoTrack.enabled);
            this.cameraStateElement.classList.toggle("text-bg-danger", !videoTrack.enabled);
        }
    }

    toggleMic() {
        if (!this.localStream) {
            this.setStatus("Camera/Mic is not ready yet");
            return;
        }

        const audioTrack = this.localStream.getAudioTracks()[0];

        if (!audioTrack) {
            this.setStatus("No microphone track found");
            return;
        }

        audioTrack.enabled = !audioTrack.enabled;
        this.updateControlStates();
    }

    toggleCamera() {
        if (!this.localStream) {
            this.setStatus("Camera/Mic is not ready yet");
            return;
        }

        const videoTrack = this.localStream.getVideoTracks()[0];

        if (!videoTrack) {
            this.setStatus("No camera track found");
            return;
        }

        videoTrack.enabled = !videoTrack.enabled;
        this.updateControlStates();
    }

    endCall() {
        console.log("Ending call...");

        // stop media
        if (this.localStream) {
            this.localStream.getTracks().forEach(track =>   track.stop());
        }

    // close peer connection
        if (this.peerConnection) {
            this.peerConnection.close();
        }

        // close websocket
        if (this.socket) {
            this.socket.close();
        }

    // clear videos
        if (this.localVideo) this.localVideo.srcObject = null;
        if (this.remoteVideo) this.remoteVideo.srcObject = null;

        this.setStatus("Call ended");

    // redirect to home after short delay
        setTimeout(() => {
            window.location.href = "/";
        }, 1000);
    }

    createPeerConnection() {
        this.peerConnection = new RTCPeerConnection({
            iceServers: [
                { urls: "stun:stun.l.google.com:19302" }
            ]
        });

        console.log("PeerConnection created");

        // Remote stream
        this.peerConnection.ontrack = (event) => {
            console.log("Remote stream received");
            this.remoteVideo.srcObject = event.streams[0];
            this.setStatus("Connected");
        };

        // ICE candidates
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendSignal({
                    type: "ice",
                    candidate: event.candidate
                });
            }
        };

        // Debug logs
        this.peerConnection.onconnectionstatechange = () => {
            console.log("Connection:", this.peerConnection.connectionState);
        };

        this.peerConnection.oniceconnectionstatechange = () => {
            console.log("ICE:", this.peerConnection.iceConnectionState);
        };
    }

    addLocalTracks() {
        this.localStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.localStream);
        });
    }

    connectWebSocket() {
        const protocol = location.protocol === "https:" ? "wss" : "ws";

        this.socket = new WebSocket(
            `${protocol}://${location.host}/ws/room/${this.roomId}/`
        );

        this.socket.onopen = () => {
            console.log("WebSocket connected");
            this.setStatus("Connected to room");

            this.sendSignal({ type: "join" });
        };

        this.socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            console.log("Received:", data);

            await this.handleSignal(data);
        };

        this.socket.onerror = (e) => {
            console.error("WebSocket error:", e);
            this.setStatus("WebSocket error");
        };

        this.socket.onclose = () => {
            console.log("WebSocket closed");
            this.setStatus("Disconnected");
        };
    }

    sendSignal(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }

    async handleSignal(data) {

        // JOIN → only one creates offer
        if (data.type === "join") {
            if (!this.hasCreatedOffer && this.peerConnection.signalingState === "stable") {
                this.hasCreatedOffer = true;

                console.log("Creating offer...");
                await this.createOffer();
            }
        }

        // OFFER
        if (data.type === "offer") {
            console.log("Offer received");

            await this.peerConnection.setRemoteDescription(data.offer);
            await this.createAnswer();
        }

        // ANSWER
        if (data.type === "answer") {
            console.log("Answer received");

            await this.peerConnection.setRemoteDescription(data.answer);
        }

        // ICE
        if (data.type === "ice") {
            if (data.candidate) {
                try {
                    await this.peerConnection.addIceCandidate(data.candidate);
                } catch (e) {
                    console.error("ICE error:", e);
                }
            }
        }
    }

    async createOffer() {
        const offer = await this.peerConnection.createOffer();
        await this.peerConnection.setLocalDescription(offer);

        this.sendSignal({
            type: "offer",
            offer: offer
        });

        console.log("Offer sent");
    }

    async createAnswer() {
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);

        this.sendSignal({
            type: "answer",
            answer: answer
        });

        console.log("Answer sent");
    }

    setStatus(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
    }
}

// 🔥 GLOBAL CONTROLLER (fix for unload bug)
let controller;

document.addEventListener("DOMContentLoaded", () => {
    controller = new RoomMediaController({
        localVideo: document.getElementById("localVideo"),
        remoteVideo: document.getElementById("remoteVideo"),
        statusElement: document.getElementById("mediaStatus"),
        micButton: document.getElementById("micBtn"),
        cameraButton: document.getElementById("cameraBtn"),
        micStateElement: document.getElementById("micState"),
        cameraStateElement: document.getElementById("cameraState")
    });

    controller.initialize();

    const micBtn = document.getElementById("micBtn");
    if (micBtn) {
        micBtn.addEventListener("click", (event) => {
            event.preventDefault();
            controller.toggleMic();
        });
    }

    const camBtn = document.getElementById("cameraBtn");
    if (camBtn) {
        camBtn.addEventListener("click", (event) => {
            event.preventDefault();
            controller.toggleCamera();
        });
    }

    const endBtn = document.getElementById("endCallBtn");

    if (endBtn) {
       endBtn.addEventListener("click", () => {
          controller.endCall();
        });
    }
});

// 🔥 CLEANUP (important)
window.addEventListener("beforeunload", () => {
    if (!controller) return;

    if (controller.localStream) {
        controller.localStream.getTracks().forEach(track => track.stop());
    }

    if (controller.peerConnection) {
        controller.peerConnection.close();
    }

    if (controller.socket) {
        controller.socket.close();
    }
});
