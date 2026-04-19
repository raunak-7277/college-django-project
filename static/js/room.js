class RoomMediaController {
    constructor(options) {
        this.localVideo = options.localVideo;
        this.remoteVideo = options.remoteVideo;
        this.statusElement = options.statusElement;

        this.localStream = null;
        this.remoteStream = new MediaStream();
        this.peerConnection = null;
        this.socket = null;

        this.roomId = window.roomConfig?.roomId || this.getRoomIdFromPath();

        this.clientId = Math.random().toString(36).substring(2);

        this.iceQueue = [];
        this.isRemoteDescriptionSet = false;
        this.isOfferCreated = false;
        this.makingOffer = false;
    }

    async initialize() {
        if (!this.localVideo) return;
        if (!this.roomId) {
            this.setStatus("Missing room id");
            return;
        }

        this.setStatus("Requesting camera & mic...");

        try {
            // 🎥 get media
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            this.localVideo.srcObject = this.localStream;

            this.createPeerConnection();
            this.addLocalTracks();
            this.connectWebSocket();

            this.setStatus("Ready for connection");

        } catch (error) {
            console.error(error);
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

        this.remoteVideo.srcObject = this.remoteStream;

        this.peerConnection.ontrack = (event) => {
            console.log("Remote track received:", event.track.kind);

            const hasTrack = this.remoteStream.getTracks().some((track) => {
                return track.id === event.track.id;
            });

            if (!hasTrack) {
                this.remoteStream.addTrack(event.track);
            }

            this.remoteVideo
                .play()
                .then(() => {
                    this.setStatus("Remote participant connected");
                })
                .catch((error) => {
                    console.warn("Remote video autoplay was blocked:", error);
                    this.setStatus("Remote stream ready. Click the video if playback is blocked.");
                });
        };

        // 📡 ICE
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendSignal({
                    type: "ice",
                    candidate: event.candidate
                });
            }
        };

        // 🔍 debug logs
        this.peerConnection.onconnectionstatechange = () => {
            console.log("Connection state:", this.peerConnection.connectionState);
        };

        this.peerConnection.oniceconnectionstatechange = () => {
            console.log("ICE state:", this.peerConnection.iceConnectionState);
        };

        this.peerConnection.onnegotiationneeded = async () => {
            if (this.isOfferCreated) {
                return;
            }

            this.isOfferCreated = true;
            await this.createOffer();
        };
    }

    getRoomIdFromPath() {
        const segments = window.location.pathname.split("/").filter(Boolean);
        return segments.length >= 2 ? segments[1] : null;
    }

    addLocalTracks() {
        this.localStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.localStream);
        });

        console.log("Local tracks added");
    }

    connectWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";

        this.socket = new WebSocket(
            `${protocol}://${window.location.host}/ws/room/${this.roomId}/`
        );

        this.socket.onopen = () => {
            console.log("WebSocket connected");
            this.setStatus("Connected to room");

            this.sendSignal({ type: "join" });
        };

        this.socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            // ❌ ignore self messages
            if (data.sender === this.clientId) return;

            console.log("Signal received:", data);

            await this.handleSignal(data);
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            this.setStatus("Signaling connection failed");
        };

        this.socket.onclose = () => {
            console.log("WebSocket disconnected");
            this.setStatus("Disconnected from signaling server");
        };
    }

    sendSignal(data) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.warn("WebSocket is not open. Dropping signal:", data.type);
            return;
        }

        data.sender = this.clientId;
        this.socket.send(JSON.stringify(data));
    }

    async handleSignal(data) {

        // 🟢 JOIN
        if (data.type === "join") {
            if (!this.isOfferCreated && this.peerConnection.signalingState === "stable") {
                setTimeout(async () => {
                    if (!this.isOfferCreated) {
                        this.isOfferCreated = true;
                        await this.createOffer();
                    }
                }, 500);
            }
        }

        if (data.type === "offer") {
            console.log("Offer received");

            const offerCollision =
                this.makingOffer || this.peerConnection.signalingState !== "stable";

            if (offerCollision) {
                const shouldIgnoreOffer = this.clientId < data.sender;

                if (shouldIgnoreOffer) {
                    console.warn("Ignoring collided offer");
                    return;
                }

                await this.peerConnection.setLocalDescription({ type: "rollback" });
            }

            await this.peerConnection.setRemoteDescription(data.offer);
            this.isRemoteDescriptionSet = true;
            this.isOfferCreated = true;

            for (let candidate of this.iceQueue) {
                await this.peerConnection.addIceCandidate(candidate);
            }
            this.iceQueue = [];

            await this.createAnswer();
        }

        if (data.type === "answer") {
            console.log("Answer received");

            await this.peerConnection.setRemoteDescription(data.answer);
            this.isRemoteDescriptionSet = true;

            for (let candidate of this.iceQueue) {
                await this.peerConnection.addIceCandidate(candidate);
            }
            this.iceQueue = [];
        }

        if (data.type === "ice") {
            if (data.candidate) {
                if (this.isRemoteDescriptionSet) {
                    await this.peerConnection.addIceCandidate(data.candidate);
                } else {
                    this.iceQueue.push(data.candidate);
                }
            }
        }
    }

    async createOffer() {
        try {
            this.makingOffer = true;
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);

            this.sendSignal({
                type: "offer",
                offer: offer
            });

            console.log("Offer sent");
        } finally {
            this.makingOffer = false;
        }
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

document.addEventListener("DOMContentLoaded", () => {
    const controller = new RoomMediaController({
        localVideo: document.getElementById("localVideo"),
        remoteVideo: document.getElementById("remoteVideo"),
        statusElement: document.getElementById("mediaStatus")
    });

    controller.initialize();
});
