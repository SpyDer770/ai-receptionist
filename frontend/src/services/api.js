const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function apiPost(path, body) {
    let response;
    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    } catch (networkError) {
        throw new Error(
            "Could not reach the server. Check your connection and that the backend is running."
        );
    }

    let data;
    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const message =
            (data && typeof data.detail === "string" && data.detail) ||
            `Request failed with status ${response.status}`;
        throw new Error(message);
    }

    return data;
}