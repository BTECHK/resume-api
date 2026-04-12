import { useEffect, useState } from "react";

export interface AppConfig {
  aiServiceUrl: string;
  candidateName: string;
  candidateTitle: string;
  candidateEmail: string;
}

const DEFAULTS: AppConfig = {
  aiServiceUrl: "",
  candidateName: "Candidate",
  candidateTitle: "Software Engineer",
  candidateEmail: "hello@example.com",
};

let cached: AppConfig | null = null;
let promise: Promise<AppConfig> | null = null;

export function getConfig(): Promise<AppConfig> {
  if (cached) return Promise.resolve(cached);
  if (!promise) {
    promise = fetch("/config.json")
      .then((r) => (r.ok ? r.json() : DEFAULTS))
      .then((c: AppConfig) => {
        cached = { ...DEFAULTS, ...c };
        return cached;
      })
      .catch(() => {
        cached = DEFAULTS;
        return cached;
      });
  }
  return promise;
}

export function useConfig(): AppConfig {
  const [config, setConfig] = useState<AppConfig>(cached ?? DEFAULTS);
  useEffect(() => {
    if (!cached) {
      getConfig().then(setConfig);
    }
  }, []);
  return config;
}
