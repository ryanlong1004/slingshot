import axios from "axios";

const API_URL = process.env.VUE_APP_API_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: API_URL,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json"
    }
});

export const playerApi = {
    async getStatus() {
        return api.get("/player/status");
    },

    async playVideo(videoPath, options = { loop: true, fullscreen: true }) {
        return api.post("/player/play", {
            video_path: videoPath,
            ...options
        });
    },

    async stopVideo() {
        return api.post("/player/stop");
    },

    async restartVideo() {
        return api.post("/player/restart");
    }
};
