function LoadingIndicator() {
    return (
        <div className="message-row message-row-ai">
            <div className="message-bubble message-bubble-ai loading-bubble">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
            </div>
        </div>
    );
}

export default LoadingIndicator;