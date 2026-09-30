import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

function MessageList({ messages }) {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div className="message-list">
            {messages.map((msg) => (
                <MessageBubble key={msg.id} sender={msg.sender} text={msg.text} failed={msg.failed} />
            ))}
            <div ref={bottomRef} />
        </div>
    );
}

export default MessageList;