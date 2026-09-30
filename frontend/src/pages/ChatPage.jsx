import Header from "../components/Header";
import MessageList from "../components/MessageList";
import MessageInput from "../components/MessageInput";
import ErrorBanner from "../components/ErrorBanner";
import LoadingIndicator from "../components/LoadingIndicator";
import { useChat } from "../hooks/useChat";

function ChatPage() {
    const { messages, loading, error, send, clear, clearError } = useChat();

    return (
        <div className="chat-page">
            <Header onClear={clear} disabled={loading} />
            <ErrorBanner message={error} onDismiss={clearError} />
            <div className="chat-body">
                <MessageList messages={messages} />
                {loading && <LoadingIndicator />}
            </div>
            <MessageInput onSend={send} disabled={loading} />
        </div>
    );
}


export default ChatPage;