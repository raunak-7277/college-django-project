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
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            this.localVideo.srcObject = this.localStream;

            this.createPeerConnection();
            this.addLocalTracks();
            this.connectWebSocket();

        } catch (err) {
            console.error("Media error:", err);
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
        };

        // ICE
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendSignal({
                    type: "ice",
                    candidate: event.candidate
                });
            }
        };

        // Debug
        this.peerConnection.onconnectionstatechange = () => {
            console.log("Connection:", this.peerConnection.connectionState);
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

            this.sendSignal({ type: "join" });
        };

        this.socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            console.log("Received:", data);

            await this.handleSignal(data);
        };
    }

    sendSignal(data) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }

    async handleSignal(data) {

        // JOIN → create offer (only once)
        if (data.type === "join") {
            if (!this.hasCreatedOffer) {
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
}

document.addEventListener("DOMContentLoaded", () => {
    const controller = new RoomMediaController({
        localVideo: document.getElementById("localVideo"),
        remoteVideo: document.getElementById("remoteVideo"),
        statusElement: document.getElementById("mediaStatus")
    });

    controller.initialize();
});