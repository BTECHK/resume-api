import { useEffect, useMemo, useRef, useState } from "react";
import { Header } from "../components/Header";
import { MessageBubble } from "../components/MessageBubble";
import { TypingIndicator } from "../components/TypingIndicator";
import { ChatInput } from "../components/ChatInput";
import { sendChat, ChatApiError } from "../lib/api";
import { useConfig } from "../lib/config";
import type { ChatMessage } from "../lib/types";

const ERROR_REPLY: ChatMessage = {
  role: "assistant",
  content:
    "Sorry, I couldn't reach the AI right now. Please try again in a moment.",
};

export function Chat() {
  const { candidateName, candidateTitle } = useConfig();

  const initials = useMemo(
    () =>
      candidateName
        .split(" ")
        .filter(Boolean)
        .map((word) => word[0]!.toUpperCase())
        .slice(0, 2)
        .join(""),
    [candidateName]
  );

  const greeting: ChatMessage = useMemo(
    () => ({
      role: "assistant",
      content: `Hi — I'm a bot trained on ${candidateName}'s resume. Ask me anything about their background, skills, or experience.`,
    }),
    [candidateName]
  );
  const [messages, setMessages] = useState<ChatMessage[]>(() => [greeting]);
  const greetingSet = useRef(false);
  useEffect(() => {
    if (!greetingSet.current) {
      greetingSet.current = true;
      setMessages([greeting]);
    }
  }, [greeting]);
  const [isLoading, setIsLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom on new message — but only if user was already near
  // the bottom (Pitfall #8 — don't steal scroll position).
  useEffect(() => {
    const el = listRef.current;
    if (!el) return;
    const nearBottom =
      el.scrollHeight - el.scrollTop - el.clientHeight < 100;
    if (nearBottom) el.scrollTop = el.scrollHeight;
  }, [messages, isLoading]);

  // Cancel any in-flight request when the Chat screen unmounts
  // (e.g. user clicks the back button to return to Landing).
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const handleSend = async (text: string) => {
    // Abort any prior in-flight request (rapid sends should cancel the older one)
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const userMsg: ChatMessage = { role: "user", content: text };
    // Cap conversation history at last 10 messages per D-10 (matches ai-service validator)
    const nextMessages = [...messages, userMsg].slice(-10);
    setMessages(nextMessages);
    setIsLoading(true);

    try {
      const response = await sendChat(nextMessages, controller.signal);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer },
      ]);
    } catch (err) {
      // Silently ignore aborts — they're a valid lifecycle event, not an error
      if (err instanceof DOMException && err.name === "AbortError") {
        return;
      }
      // Anything else (ChatApiError, network failure, parse error) → inline error reply
      if (err instanceof ChatApiError) {
        console.error("[chat] ChatApiError:", err.message, err.status);
      } else {
        console.error("[chat] Unexpected error:", err);
      }
      setMessages((prev) => [...prev, ERROR_REPLY]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[100dvh] bg-[var(--color-canvas)] dark:bg-[var(--color-canvas-dark)]">
      <Header initials={initials || "?"} title={candidateTitle} />

      <div ref={listRef} className="flex-1 overflow-y-auto">
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
