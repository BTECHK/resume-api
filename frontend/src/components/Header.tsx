import { Link } from "react-router";

interface HeaderProps {
  /** Initials shown in the avatar circle (e.g. "JD" for "Jane Doe"). */
  initials: string;
  /** Candidate professional title shown next to the avatar. */
  title: string;
}

export function Header({ initials, title }: HeaderProps) {
  return (
    <header
      className="
        sticky top-0 z-10
        backdrop-blur-xl bg-white/70 dark:bg-[#1c1c1e]/70
        border-b border-black/5 dark:border-white/10
      "
    >
      <div className="mx-auto max-w-3xl flex items-center gap-3 px-4 py-3 sm:px-6">
        <Link
          to="/"
          aria-label="Back to landing"
          className="
            inline-flex items-center justify-center
            h-9 w-9 rounded-full
            text-[var(--color-ink)] dark:text-white
            hover:bg-black/5 dark:hover:bg-white/10
            transition-colors
          "
        >
          {/* Inline back arrow — Apple-style chevron */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="h-5 w-5"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M12.79 5.23a.75.75 0 0 1 0 1.06L9.06 10l3.73 3.71a.75.75 0 1 1-1.06 1.06l-4.24-4.24a.75.75 0 0 1 0-1.06l4.24-4.24a.75.75 0 0 1 1.06 0Z"
              clipRule="evenodd"
            />
          </svg>
        </Link>

        <div
          className="
            inline-flex items-center justify-center
            h-9 w-9 rounded-full
            bg-[var(--color-accent)] text-white
            text-sm font-semibold
            shadow-[var(--shadow-card)]
          "
          aria-hidden="true"
        >
          {initials}
        </div>

        <h2 className="text-base sm:text-lg font-medium truncate text-[var(--color-ink)] dark:text-white">
          {title}
        </h2>
      </div>
    </header>
  );
}
