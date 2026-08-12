const DEFAULT_BASE_URL = "http://localhost:8000/api";

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

function withProtocol(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return trimmed;
  }
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }
  return `http://${trimmed}`;
}

function normalizeBaseUrl(value: string): string {
  const safe = withProtocol(value).replace(/\/+$/, "");
  return safe;
}

function getBaseUrlCandidates(): string[] {
  const primary = normalizeBaseUrl(process.env.NEXT_PUBLIC_BACKEND_API_URL || DEFAULT_BASE_URL);
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

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const baseUrls = getBaseUrlCandidates();

  const headers = new Headers(options.headers);
  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  let body: BodyInit | null | undefined = options.body;
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.json);
  }

  let lastNetworkError: unknown = null;
  for (const baseUrl of baseUrls) {
    const url = `${baseUrl}${path}${toQueryString(options.query)}`;
    try {
      const response = await fetch(url, {
        method: options.method || "GET",
        headers,
        body,
      });

      const text = await response.text();
      const payload = text ? safeParse(text) : null;

      if (!response.ok) {
        throw new ApiError(
          typeof payload === "object" && payload && "message" in payload
            ? String((payload as Record<string, unknown>).message)
            : `Request failed with status ${response.status}`,
          response.status,
          payload,
        );
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
    "Could not reach backend API. Verify backend_v5 is running and NEXT_PUBLIC_BACKEND_API_URL is correct.",
    0,
    lastNetworkError,
  );
}

function safeParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}
