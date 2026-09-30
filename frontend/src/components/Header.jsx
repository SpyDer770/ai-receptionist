function Header({ onClear, disabled }) {
    return (
        <header className="chat-header">
            <h1>AI Receptionist</h1>
            <button className="clear-button" onClick={onClear} disabled={disabled}>
                Clear conversation
            </button>
        </header>
    );
}

export default Header;