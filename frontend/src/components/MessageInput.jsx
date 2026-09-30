import { useState } from "react";

function MessageInput({ onSend, disabled }) {
    const [text, setText] = useState("");

    function handleSubmit(e) {
        e.preventDefault();
        const trimmed = text.trim();
        if (!trimmed || disabled) return;
        onSend(trimmed);
        setText("");
    }

    return (
        <form className="message-input-row" onSubmit={handleSubmit}>
            <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type a message..."
                disabled={disabled}
                aria-label="Message"
            />
            <button type="submit" disabled={disabled || !text.trim()}>
                {disabled ? "Sending..." : "Send"}
            </button>
        </form>
    );
}

export default MessageInput;