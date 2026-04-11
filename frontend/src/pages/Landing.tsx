import { Link } from "react-router";

const CANDIDATE_NAME = import.meta.env.VITE_CANDIDATE_NAME || "Candidate";
const CANDIDATE_TITLE =
  import.meta.env.VITE_CANDIDATE_TITLE || "Software Engineer";
const CANDIDATE_EMAIL =
  import.meta.env.VITE_CANDIDATE_EMAIL || "hello@example.com";

const MAILTO_HREF = `mailto:${CANDIDATE_EMAIL}?subject=${encodeURIComponent(
  `Resume inquiry from ${CANDIDATE_NAME}`
)}`;

export function Landing() {
  return (
    <main className="min-h-[100dvh] flex items-center justify-center px-6 py-12">
      <div className="mx-auto max-w-2xl w-full text-center">
        {/* Hero */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-[var(--color-ink)] dark:text-white">
          {CANDIDATE_NAME}
        </h1>
        <h2 className="mt-3 text-xl sm:text-2xl text-[var(--color-ink-muted)] font-normal">
          {CANDIDATE_TITLE}
        </h2>

        <p className="mt-6 text-base sm:text-lg text-[var(--color-ink-muted)] max-w-xl mx-auto">
          Ask my AI-powered resume bot anything about my background — or send a
          quick email to start a conversation.
        </p>

        {/* CTAs */}
        <div className="mt-10 flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3 sm:gap-4">
          <Link
            to="/chat"
            className="
              inline-flex items-center justify-center
              rounded-full
              bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)]
              text-white font-medium
              px-7 py-3.5
              text-base
              shadow-[var(--shadow-hero)]
              transition-colors
            "
          >
            {/* Chat icon */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-5 w-5 mr-2"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 2c-4.97 0-9 3.358-9 7.5 0 1.694.682 3.252 1.821 4.503-.214.99-.751 1.82-1.343 2.404a.75.75 0 0 0 .533 1.291c1.86 0 3.32-.604 4.32-1.276A10.6 10.6 0 0 0 10 17c4.97 0 9-3.358 9-7.5S14.97 2 10 2Z"
                clipRule="evenodd"
              />
            </svg>
            Chat With My Resume
          </Link>

          <a
            href={MAILTO_HREF}
            className="
              inline-flex items-center justify-center
              rounded-full
              bg-[var(--color-surface)] dark:bg-[var(--color-surface-dark)]
              text-[var(--color-ink)] dark:text-white
              font-medium
              px-7 py-3.5
              text-base
              border border-black/10 dark:border-white/15
              hover:bg-black/[0.03] dark:hover:bg-white/5
              shadow-[var(--shadow-card)]
              transition-colors
            "
          >
            {/* Email icon */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-5 w-5 mr-2"
              aria-hidden="true"
            >
              <path d="M3 4a2 2 0 0 0-2 2v1.161l8.441 4.221a1.25 1.25 0 0 0 1.118 0L19 7.162V6a2 2 0 0 0-2-2H3Z" />
              <path d="m19 8.839-7.77 3.885a2.75 2.75 0 0 1-2.46 0L1 8.839V14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8.839Z" />
            </svg>
            Email My Resume
          </a>
        </div>
      </div>
    </main>
  );
}
