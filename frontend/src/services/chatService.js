import { apiPost } from "./api";

export async function sendMessage(message) {
    return apiPost("/chat", { message });
}