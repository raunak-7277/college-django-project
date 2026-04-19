class RoomMediaController {
    constructor(options) {
        this.localVideo = options.localVideo;
        this.remoteVideo = options.remoteVideo;
        this.statusElement = options.statusElement;

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

            this.setStatus("Ready");

        } catch (err) {
            console.error("Media error:", err);
            this.setStatus("Camera/Mic access failed");
        }
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
        statusElement: document.getElementById("mediaStatus")
    });

    controller.initialize();
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