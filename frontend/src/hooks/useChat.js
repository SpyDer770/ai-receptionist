import { useState } from "react";
import { sendMessage } from "../services/chatService";

let nextId = 1;
function makeId() {
    return nextId++;
}

const GREETING = {
    id: makeId(),
    sender: "ai",
    text: "Hello! I'm your AI receptionist. I can help you book, check, or cancel an appointment. How can I help you today?",
};

export function useChat() {
    const [messages, setMessages] = useState([GREETING]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    async function send(text) {
        setError(null);
        const userMessageId = makeId();
        setMessages((prev) => [...prev, { id: userMessageId, sender: "user", text, failed: false }]);
        setLoading(true);

        try {
            const response = await sendMessage(text);
            setMessages((prev) => [
                ...prev,
                { id: makeId(), sender: "ai", text: response.reply },
            ]);
        } catch (err) {
            setError(err.message);
            setMessages((prev) =>
                prev.map((m) => (m.id === userMessageId ? { ...m, failed: true } : m))
            );
        } finally {
            setLoading(false);
        }
    }

    function clear() {
        setMessages([{ ...GREETING, id: makeId() }]);
        setError(null);
    }

    return { messages, loading, error, send, clear, clearError: () => setError(null) };
}