---
phase: 06
plan: 06-02
plan_name: landing-and-chat-ui
subsystem: frontend
tags: [frontend, react, tailwind, apple-hig, ui]
requires:
  - 06-01 (frontend scaffold + router + index.css @theme tokens)
provides:
  - Landing page (hero + two CTAs per D-08)
  - Chat screen shell (header + message list + typing indicator + input) per D-09
  - Reusable components/ directory (Header, MessageBubble, TypingIndicator, ChatInput)
  - CHAT-02 polished design surface
  - CHAT-03 mobile-responsive utilities (9 sm:/md: matches across src/)
  - CHAT-05 auto-greeting literal wired to VITE_CANDIDATE_NAME
  - CHAT-07 landing page with two CTAs
  - CHAT-08 Landing -> Chat navigation via Link
affects:
  - frontend/src/pages/Landing.tsx (replaced stub)
  - frontend/src/pages/Chat.tsx (replaced stub)
  - frontend/src/components/* (new directory)
tech-stack:
  added: []
  patterns:
    - Inline SVG icons (zero bundle cost, no icon library)
    - Apple HIG tokens consumed via Tailwind arbitrary-value utilities (var(--color-accent), etc.)
    - Glass-blur sticky header + input with backdrop-blur-xl
    - Pure-CSS @keyframes for typing-bounce animation
    - 100dvh instead of 100vh for iOS Safari safety
    - nearBottom heuristic auto-scroll (do not steal user scroll position)
    - verbatimModuleSyntax-safe type-only imports (import type { KeyboardEvent, ChangeEvent })
key-files:
  created:
    - frontend/src/components/Header.tsx (66 lines)
    - frontend/src/components/MessageBubble.tsx (32 lines)
    - frontend/src/components/TypingIndicator.tsx (33 lines)
    - frontend/src/components/ChatInput.tsx (116 lines)
  modified:
    - frontend/src/pages/Landing.tsx (95 lines, overwritten stub)
    - frontend/src/pages/Chat.tsx (92 lines, overwritten stub)
decisions:
  - D-02 Apple HIG aesthetic applied via index.css @theme tokens
  - D-08 Landing copy + CTAs: Link to /chat, mailto anchor with inquiry subject
  - D-09 Chat layout: glass header + scrollable list + typing indicator + bottom-fixed input
  - D-11 Zero analytics / zero icon libraries enforced (inline SVG only)
  - D-13 No unit tests; build smoke + grep acceptance is the verification bar
metrics:
  tasks_completed: 2
  files_created: 4
  files_modified: 2
  total_new_lines: 434
  commits: 2
  build_status: green
  responsive_utility_count: 9
---

# Phase 6 Plan 2: Landing Page + Chat Screen UI Summary

## One-liner

Replaced Landing and Chat page stubs with full Apple-HIG-styled UI (hero + two CTAs on Landing; glass header + message bubbles + typing indicator + bottom-fixed input on Chat), backed by a new `frontend/src/components/` directory housing four reusable components — all using hardcoded sample messages so visual review works without any API wiring.

## File tree changes

```
frontend/src/
├── components/                 (NEW directory)
│   ├── Header.tsx              (66 lines) — sticky glass header, avatar, back Link
│   ├── MessageBubble.tsx       (32 lines) — user/assistant variants
│   ├── TypingIndicator.tsx     (33 lines) — 3-dot CSS @keyframes animation
│   └── ChatInput.tsx           (116 lines) — textarea + Enter/Shift+Enter + 500-char counter + send button
├── pages/
│   ├── Landing.tsx             (95 lines) — OVERWRITTEN: hero + 2 CTAs per D-08
│   └── Chat.tsx                (92 lines) — OVERWRITTEN: full Chat shell with hardcoded messages
├── index.css                   (unchanged)
├── main.tsx                    (unchanged)
└── vite-env.d.ts               (unchanged)
```

Total: 4 new files, 2 overwrites, 434 lines of new code.

## Requirement status

| Req ID  | Name                                  | Status            | Notes |
| ------- | ------------------------------------- | ----------------- | ----- |
| CHAT-02 | Polished chat design                  | COMPLETE          | Bubbles, glass header, typing indicator all rendered visually |
| CHAT-03 | Mobile responsive                     | COMPLETE          | 9 `sm:`/`md:` matches across src/pages + src/components (threshold ≥ 8), `100dvh` everywhere |
| CHAT-05 | Auto-greeting                         | STRUCTURALLY DONE | Greeting literal `"Hi — I'm a bot trained on ${VITE_CANDIDATE_NAME}'s resume..."` seeds `initialMessages[0]`; Plan 06-03 keeps same hook shape |
| CHAT-07 | Landing page with 2 CTAs              | COMPLETE          | Hero + tagline + "Chat With My Resume" Link + "Email My Resume" mailto anchor |
| CHAT-08 | Landing → Chat navigation             | COMPLETE          | `<Link to="/chat">` wired |

## Acceptance criteria evidence

All plan `<acceptance>` items pass. Key grep evidence:

```
grep -q 'VITE_CANDIDATE_NAME'     frontend/src/pages/Landing.tsx   PASS
grep -q 'mailto:'                 frontend/src/pages/Landing.tsx   PASS
grep -q 'Resume inquiry from'     frontend/src/pages/Landing.tsx   PASS
grep -q 'to="/chat"'              frontend/src/pages/Landing.tsx   PASS
grep -q 'from "react-router"'     frontend/src/pages/Landing.tsx   PASS
grep -q 'min-h-\[100dvh\]'        frontend/src/pages/Landing.tsx   PASS
grep -q 'h-\[100dvh\]'            frontend/src/pages/Chat.tsx      PASS
grep -q "Hi — I'm a bot trained on" frontend/src/pages/Chat.tsx    PASS
grep -q 'nearBottom'              frontend/src/pages/Chat.tsx      PASS
grep -q 'TypingIndicator'         frontend/src/pages/Chat.tsx      PASS
grep -q 'MessageBubble'           frontend/src/pages/Chat.tsx      PASS
grep -q 'Header'                  frontend/src/pages/Chat.tsx      PASS
grep -q 'ChatInput'               frontend/src/pages/Chat.tsx      PASS
! grep -R 'react-router-dom'      frontend/src/                    PASS
! grep -R 'react-icons|lucide-react|@heroicons' frontend/src/      PASS
! grep -R 'h-screen'              frontend/src/                    PASS
grep -RE '(sm:|md:)' frontend/src/pages/ frontend/src/components/ | wc -l  => 9 (>=8)
cd frontend && npm run build                                        PASS (built in 427ms)
```

Build output:
```
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-CI2jlJiX.css   18.97 kB │ gzip:  4.41 kB
dist/assets/index-kq0a8hY3.js   292.05 kB │ gzip: 92.73 kB
```

## Deviations from plan

**None.** Plan executed exactly as written — component code, page code, imports, and file paths match the plan verbatim. No auto-fixes under Rules 1-3 triggered; no architectural questions (Rule 4) raised. All four components and both pages copy-pasted from the plan's code blocks without edits.

## Pitfalls encountered

None tripped. Pre-emptively handled by the plan's code blocks:

- **Pitfall #2 (bare border):** All borders use explicit color classes (`border-black/5`, `border-white/10`, `border-black/10`, `border-white/15`) — `index.css` also sets `--default-border-color` as a backstop.
- **Pitfall #7 (100vh):** Every full-height container uses `100dvh` — `Landing` uses `min-h-[100dvh]`, `Chat` uses `h-[100dvh]`. Grep confirms no `h-screen` anywhere in `frontend/src/`.
- **Pitfall #8 (scroll steal):** `Chat.tsx` `useEffect` checks `nearBottom` before auto-scrolling.
- **Pitfall #11 (verbatimModuleSyntax):** `ChatInput.tsx` uses `import { useState, type KeyboardEvent, type ChangeEvent } from "react"` — `tsc -b` passed first try.

## Auth gates

None — this plan is entirely UI scaffolding with no network calls.

## Commits produced

| SHA      | Type | Message |
| -------- | ---- | ------- |
| ebeccdb  | feat | feat(06-02): add Header, MessageBubble, TypingIndicator, ChatInput components |
| 319b260  | feat | feat(06-02): landing + chat UI with Apple HIG design |

Both committed with `--no-verify` per orchestrator guidance (pre-commit hooks are not configured for Phase 6; flag used defensively).

## Notes for Plan 06-03 executor (API wiring)

Plan 06-03 needs to replace the hardcoded stubs with real ai-service calls. Everything you need is already in place:

### Contract surface that will survive into 06-03

1. **`ChatInput` component:** Already accepts `onSend: (text: string) => void` and `disabled?: boolean` — do not change the component. Just swap the body of `handleSend` in `Chat.tsx`.

2. **`UIMessage` interface in `Chat.tsx`:** `{ role: "user" | "assistant"; content: string }` — keep this shape. It matches the ai-service OpenAI-compatible format from Plan 04-03.

3. **`messages` state:** Already a `useState<UIMessage[]>`. The auto-scroll `useEffect` is indexed on `[messages, isLoading]` — any new message or loading state change triggers it.

4. **`isLoading` state:** Already wired — `ChatInput` receives it as `disabled`, `TypingIndicator` shows when true. Keep the pattern: `setIsLoading(true)` before fetch, `setIsLoading(false)` in the `finally`.

### What to rip out in 06-03

- Delete lines in `Chat.tsx`:
  - `const initialMessages: UIMessage[] = [ greeting, { role: "user", ... }, { role: "assistant", ... } ];`
  - Replace with: `const initialMessages: UIMessage[] = [greeting];`
- Replace the entire body of `handleSend`:
  - Remove the `setTimeout` stub
  - Wire to `sendChat()` (or whatever the 06-03 fetch helper is named) using `VITE_AI_SERVICE_URL`
  - Preserve the `setMessages(prev => [...prev, { role: "user", content: text }])` line
  - Add error handling that pushes an error-role bubble or similar (see CHAT-06 in REQUIREMENTS.md)

### What NOT to touch

- `initials` computation — env-driven, works for any candidate name.
- `Header`/`MessageBubble`/`TypingIndicator`/`ChatInput` — pure presentational, no API concerns.
- The JSX tree in `Chat.tsx`'s `return` — layout is locked per D-09.
- `Landing.tsx` — nothing to do in 06-03, it's fully static.

### Env vars available

- `import.meta.env.VITE_CANDIDATE_NAME` — used in greeting literal
- `import.meta.env.VITE_CANDIDATE_TITLE` — used in Chat `Header` title prop
- `import.meta.env.VITE_CANDIDATE_EMAIL` — used in Landing mailto
- `import.meta.env.VITE_AI_SERVICE_URL` — **NOT YET USED** — Plan 06-03 must read this for the fetch target

### Known gotchas for 06-03

- `tsconfig.app.json` has `verbatimModuleSyntax: true` — fetch helpers must use `import type { ... }` for any type-only imports (`RequestInit`, etc.).
- React Router imports are from `"react-router"` not `"react-router-dom"` — see Plan 06-01 SUMMARY. Phase 6 has a negative-grep acceptance test for this that will break your build if you slip.
- The `nearBottom` heuristic in the scroll `useEffect` should stay — don't simplify it to unconditional scroll.
- Use `h-[100dvh]` not `h-screen` — Plan has a negative grep for `h-screen` across `frontend/src/`.

## Self-Check: PASSED

- [x] `frontend/src/components/Header.tsx` FOUND
- [x] `frontend/src/components/MessageBubble.tsx` FOUND
- [x] `frontend/src/components/TypingIndicator.tsx` FOUND
- [x] `frontend/src/components/ChatInput.tsx` FOUND
- [x] `frontend/src/pages/Landing.tsx` FOUND (overwritten)
- [x] `frontend/src/pages/Chat.tsx` FOUND (overwritten)
- [x] Commit `ebeccdb` FOUND in git log
- [x] Commit `319b260` FOUND in git log
- [x] `cd frontend && npm run build` exits 0
- [x] All `<acceptance>` grep commands pass
