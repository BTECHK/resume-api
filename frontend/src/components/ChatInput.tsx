import { useState, type KeyboardEvent, type ChangeEvent } from "react";

interface ChatInputProps {
  /** Called when the user submits a non-empty, valid message. */
  onSend: (text: string) => void;
  /** When true, the input is disabled (e.g. while awaiting bot response). */
  disabled?: boolean;
}

const MAX_CHARS = 500;

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [text, setText] = useState("");

  const trimmed = text.trim();
  const length = text.length;
  const tooLong = length > MAX_CHARS;
  const canSend = !disabled && trimmed.length > 0 && !tooLong;

  const handleSubmit = () => {
    if (!canSend) return;
    onSend(trimmed);
    setText("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter sends; Shift+Enter inserts a newline (D-09)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  // Counter color: muted by default, warning at 450, red at 500+
  const counterColor = tooLong
    ? "text-red-500"
    : length >= 450
    ? "text-amber-500"
    : "text-[var(--color-ink-muted)]";

  return (
    <div
      className="
        sticky bottom-0
        backdrop-blur-xl bg-white/80 dark:bg-[#1c1c1e]/80
        border-t border-black/5 dark:border-white/10
        px-4 py-3 sm:px-6
      "
    >
      <div className="mx-auto max-w-3xl">
        <div
          className="
            flex items-end gap-2
            rounded-[var(--radius-bubble)]
            bg-[var(--color-surface)] dark:bg-[var(--color-surface-dark)]
            shadow-[var(--shadow-card)]
            px-3 py-2
          "
        >
          <textarea
            value={text}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
            placeholder="Ask about background, skills, or experience…"
            aria-label="Chat message"
            className="
              flex-1 resize-none bg-transparent outline-none
              text-[15px] leading-relaxed
              text-[var(--color-ink)] dark:text-white
              placeholder:text-[var(--color-ink-muted)]
              max-h-32
              disabled:opacity-50
            "
          />
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSend}
            aria-label="Send message"
            className="
              inline-flex items-center justify-center
              h-9 w-9 rounded-full
              bg-[var(--color-accent)] text-white
              hover:bg-[var(--color-accent-hover)]
              disabled:bg-[var(--color-ink-muted)] disabled:cursor-not-allowed
              transition-colors
              shrink-0
            "
          >
            {/* Inline send arrow */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-4 w-4"
              aria-hidden="true"
            >
              <path d="M3.105 3.105a.75.75 0 0 1 .815-.165l13.5 5.25a.75.75 0 0 1 0 1.4l-13.5 5.25a.75.75 0 0 1-1.02-.882L4.5 10 2.9 4.042a.75.75 0 0 1 .205-.937Z" />
            </svg>
          </button>
        </div>

        {/* Character counter */}
        <div className={`mt-1 text-xs text-right ${counterColor}`}>
          {length}/{MAX_CHARS}
        </div>
      </div>
    </div>
  );
}
