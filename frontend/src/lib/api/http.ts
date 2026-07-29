import { getEnv } from "@/lib/env";

export type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  token?: string;
  query?: Record<string, string | number | boolean | undefined | null>;
  json?: unknown;
  body?: BodyInit;
  headers?: HeadersInit;
};

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

function toQueryString(query: RequestOptions["query"]): string {
  if (!query) {
    return "";
  }
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) {
      continue;
    }
    params.set(key, String(value));
  }
  const raw = params.toString();
  return raw ? `?${raw}` : "";
}

function safeParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function baseUrlCandidates(): string[] {
  const primary = getEnv().NEXT_PUBLIC_API_URL.replace(/\/+$/, "");
  const candidates = [primary];
  try {
    const parsed = new URL(primary);
    if (parsed.hostname === "localhost") {
      parsed.hostname = "127.0.0.1";
      candidates.push(parsed.toString().replace(/\/+$/, ""));
    } else if (parsed.hostname === "127.0.0.1") {
      parsed.hostname = "localhost";
      candidates.push(parsed.toString().replace(/\/+$/, ""));
    }
  } catch {
    return candidates;
  }
  return candidates;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  let body: BodyInit | undefined = options.body;
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.json);
  }

  let lastNetworkError: unknown = null;

  for (const base of baseUrlCandidates()) {
    try {
      const response = await fetch(`${base}${path}${toQueryString(options.query)}`, {
        method: options.method || "GET",
        headers,
        body,
      });

      const text = await response.text();
      const payload = text ? safeParse(text) : null;

      if (!response.ok) {
        const message =
          typeof payload === "object" &&
          payload &&
          "message" in payload &&
          typeof (payload as { message: unknown }).message === "string"
            ? (payload as { message: string }).message
            : `Request failed (${response.status})`;
        throw new ApiError(message, response.status, payload);
      }

      return payload as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      lastNetworkError = error;
    }
  }

  throw new ApiError(
    "No se pudo conectar con el backend. Arranca `uvicorn` en el puerto 8000 y revisa NEXT_PUBLIC_API_URL.",
    0,
    lastNetworkError,
  );
}
