function MessageBubble({ sender, text, failed }) {
    const isUser = sender === "user";

    return (
        <div className={`message-row ${isUser ? "message-row-user" : "message-row-ai"}`}>
            <div
                className={`message-bubble ${isUser ? "message-bubble-user" : "message-bubble-ai"} ${failed ? "message-bubble-failed" : ""
                    }`}
            >
                {text}
                {failed && <div className="message-failed-note">Not delivered</div>}
            </div>
        </div>
    );
}

export default MessageBubble;