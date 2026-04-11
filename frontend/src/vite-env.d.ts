/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_AI_SERVICE_URL: string;
  readonly VITE_CANDIDATE_NAME: string;
  readonly VITE_CANDIDATE_TITLE: string;
  readonly VITE_CANDIDATE_EMAIL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
