import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import MessageInput from "./MessageInput";

describe("MessageInput", () => {
    it("does not call onSend when the input is empty", () => {
        const onSend = vi.fn();
        render(<MessageInput onSend={onSend} disabled={false} />);

        fireEvent.click(screen.getByRole("button", { name: /send/i }));

        expect(onSend).not.toHaveBeenCalled();
    });

    it("does not call onSend for whitespace-only input", () => {
        const onSend = vi.fn();
        render(<MessageInput onSend={onSend} disabled={false} />);

        const input = screen.getByPlaceholderText(/type a message/i);
        fireEvent.change(input, { target: { value: "   " } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));

        expect(onSend).not.toHaveBeenCalled();
    });

    it("calls onSend with trimmed text and clears the input", () => {
        const onSend = vi.fn();
        render(<MessageInput onSend={onSend} disabled={false} />);

        const input = screen.getByPlaceholderText(/type a message/i);
        fireEvent.change(input, { target: { value: "  Hello  " } });
        fireEvent.click(screen.getByRole("button", { name: /send/i }));

        expect(onSend).toHaveBeenCalledWith("Hello");
        expect(input.value).toBe("");
    });

    it("disables the input and button when disabled prop is true", () => {
        render(<MessageInput onSend={() => { }} disabled={true} />);
        expect(screen.getByPlaceholderText(/type a message/i)).toBeDisabled();
        expect(screen.getByRole("button")).toBeDisabled();
    });
});