import type { ChatMessage, ChatRequest, ChatResponse } from "./types";
import { getConfig } from "./config";

export class ChatApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ChatApiError";
    this.status = status;
  }
}

/**
 * Send a chat message to the ai-service /chat endpoint.
 *
 * @param messages Up to 10 messages; last must be from the user. Caller is
 *                 responsible for slicing — sendChat does NOT slice.
 * @param signal   Optional AbortSignal — pass AbortController.signal to cancel
 *                 in-flight requests on unmount or when a new send arrives.
 *
 * Throws:
 *   - DOMException("AbortError") when aborted (caller should silently ignore)
 *   - ChatApiError on validation failure, network failure, or non-2xx response
 */
export async function sendChat(
  messages: ChatMessage[],
  signal?: AbortSignal
): Promise<ChatResponse> {
  // Client-side validation — mirrors ai-service Pydantic validators.
  // Catches mistakes early and gives a friendlier error than the server's 422.
  if (messages.length === 0) {
    throw new ChatApiError("No messages to send");
  }
  if (messages.length > 10) {
    throw new ChatApiError("Too many messages — max 10");
  }
  if (messages[messages.length - 1]!.role !== "user") {
    throw new ChatApiError("Last message must be from the user");
  }
  for (const m of messages) {
    const trimmed = m.content.trim();
    if (trimmed.length === 0) {
      throw new ChatApiError("Message content cannot be empty");
    }
    if (trimmed.length > 500) {
      throw new ChatApiError("Message content cannot exceed 500 characters");
    }
  }

  const { aiServiceUrl } = await getConfig();
  if (!aiServiceUrl) {
    throw new ChatApiError(
      "AI service URL is not configured. Set AI_SERVICE_URL env var on the container."
    );
  }

  const body: ChatRequest = { messages };

  let response: Response;
  try {
    response = await fetch(`${aiServiceUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw err; // Let caller handle abort specifically (no toast/UI)
    }
    throw new ChatApiError(
      "Couldn't reach the AI service. Check your connection and try again."
    );
  }

  if (!response.ok) {
    throw new ChatApiError(
      `AI service returned ${response.status}`,
      response.status
    );
  }

  return (await response.json()) as ChatResponse;
}
