export function TypingIndicator() {
  return (
    <div className="flex w-full justify-start" aria-label="Bot is typing">
      <div
        className="
          inline-flex items-center gap-1.5
          rounded-[var(--radius-bubble)]
          bg-[var(--color-surface)] dark:bg-[var(--color-surface-dark)]
          px-4 py-3
          shadow-[var(--shadow-card)]
        "
      >
        <span className="typing-dot" />
        <span className="typing-dot" style={{ animationDelay: "0.15s" }} />
        <span className="typing-dot" style={{ animationDelay: "0.3s" }} />
      </div>
      <style>{`
        .typing-dot {
          width: 6px;
          height: 6px;
          background-color: var(--color-ink-muted);
          border-radius: 9999px;
          display: inline-block;
          animation: typing-bounce 1.2s infinite ease-in-out;
        }
        @keyframes typing-bounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
