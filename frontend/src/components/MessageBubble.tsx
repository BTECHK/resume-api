interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`
          max-w-[85%] sm:max-w-[75%]
          rounded-[var(--radius-bubble)]
          px-4 py-2.5
          text-[15px] leading-relaxed
          shadow-[var(--shadow-card)]
          whitespace-pre-wrap break-words
          ${
            isUser
              ? "bg-[var(--color-accent)] text-white"
              : "bg-[var(--color-surface)] text-[var(--color-ink)] dark:bg-[var(--color-surface-dark)] dark:text-white"
          }
        `}
      >
        {content}
      </div>
    </div>
  );
}
