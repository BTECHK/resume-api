import { useEffect, useRef, useState } from "react";
import { Header } from "../components/Header";
import { MessageBubble } from "../components/MessageBubble";
import { TypingIndicator } from "../components/TypingIndicator";
import { ChatInput } from "../components/ChatInput";

const CANDIDATE_NAME = import.meta.env.VITE_CANDIDATE_NAME || "Candidate";
const CANDIDATE_TITLE =
  import.meta.env.VITE_CANDIDATE_TITLE || "Software Engineer";

// Compute initials from candidate name (e.g. "Jane Doe" → "JD")
const initials = CANDIDATE_NAME.split(" ")
  .filter(Boolean)
  .map((word) => word[0]!.toUpperCase())
  .slice(0, 2)
  .join("");

interface UIMessage {
  role: "user" | "assistant";
  content: string;
}

const greeting: UIMessage = {
  role: "assistant",
  content: `Hi — I'm a bot trained on ${CANDIDATE_NAME}'s resume. Ask me anything about their background, skills, or experience.`,
};

// HARDCODED for Plan 06-02 visual review. Plan 06-03 will reduce this back
// to `[greeting]` and wire `handleSend` to ai-service.
const initialMessages: UIMessage[] = [
  greeting,
  { role: "user", content: "What languages do you know?" },
  {
    role: "assistant",
    content:
      "I primarily work with TypeScript, Python, and Go. (This is a hardcoded sample reply — Plan 06-03 wires real responses.)",
  },
];

export function Chat() {
  const [messages, setMessages] = useState<UIMessage[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new message — but only if user was already near
  // the bottom (Pitfall #8 — don't steal scroll position).
  useEffect(() => {
    const el = listRef.current;
    if (!el) return;
    const nearBottom =
      el.scrollHeight - el.scrollTop - el.clientHeight < 100;
    if (nearBottom) el.scrollTop = el.scrollHeight;
  }, [messages, isLoading]);

  // STUB: Plan 06-03 will replace this entire body with real AI calls.
  const handleSend = (text: string) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);
    // Simulate a fake reply after 600ms so visual review shows the typing indicator
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "(Stub reply — Plan 06-03 will call ai-service /chat for real responses.)",
        },
      ]);
      setIsLoading(false);
    }, 600);
  };

  return (
    <div className="flex flex-col h-[100dvh] bg-[var(--color-canvas)] dark:bg-[var(--color-canvas-dark)]">
      <Header initials={initials || "?"} title={CANDIDATE_TITLE} />

      <div
        ref={listRef}
        className="flex-1 overflow-y-auto"
      >
        <div className="mx-auto max-w-3xl flex flex-col gap-3 px-4 py-6 sm:px-6">
          {messages.map((m, i) => (
            <MessageBubble key={i} role={m.role} content={m.content} />
          ))}
          {isLoading && <TypingIndicator />}
        </div>
      </div>

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
