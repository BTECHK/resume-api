// Must match ai-service/main.py Pydantic models exactly.
// Source of truth: ai-service/main.py lines 159–196.
// If you change one, change both. Mismatch will surface as a 422 from ai-service.

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string; // 1-500 chars, trimmed, non-empty (ai-service security.py enforces server-side)
}

export interface ChatRequest {
  messages: ChatMessage[]; // length 1-10, last must be role="user"
}

export interface ChatSource {
  chunk: string;
  relevance: number;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  model_used: string; // "gemini-2.5-flash" by default
  message_count: number;
}
