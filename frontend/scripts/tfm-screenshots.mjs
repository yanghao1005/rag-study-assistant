/**
 * One-off TFM screenshots. Reads backend/.env (service role). Does not print secrets.
 * Usage: pnpm exec node scripts/tfm-screenshots.mjs
 */
import { chromium } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "../..");
const outDir = path.join(root, "docs", "tfm", "figures", "screenshots");
const USER_ID = "664aee8b-3888-4cc9-a7e8-b840f73a13f3";
const SUBJECT_ID = "d114e19b-de11-40ce-a089-87e04887f7fc";
const BASE = "http://localhost:3000";
const MAX_CHUNK_SIZE = 3180;

function loadEnv(file) {
  const out = {};
  if (!fs.existsSync(file)) {
    return out;
  }
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) {
      continue;
    }
    const i = trimmed.indexOf("=");
    out[trimmed.slice(0, i).trim()] = trimmed.slice(i + 1).trim().replace(/^["']|["']$/g, "");
  }
  return out;
}

function createChunks(key, value) {
  let encodedValue = encodeURIComponent(value);
  if (encodedValue.length <= MAX_CHUNK_SIZE) {
    return [{ name: key, value }];
  }
  const chunks = [];
  while (encodedValue.length > 0) {
    let encodedChunkHead = encodedValue.slice(0, MAX_CHUNK_SIZE);
    const lastEscapePos = encodedChunkHead.lastIndexOf("%");
    if (lastEscapePos > MAX_CHUNK_SIZE - 3) {
      encodedChunkHead = encodedChunkHead.slice(0, lastEscapePos);
    }
    let valueHead = "";
    while (encodedChunkHead.length > 0) {
      try {
        valueHead = decodeURIComponent(encodedChunkHead);
        break;
      } catch (error) {
        if (error instanceof URIError && encodedChunkHead.at(-3) === "%" && encodedChunkHead.length > 3) {
          encodedChunkHead = encodedChunkHead.slice(0, encodedChunkHead.length - 3);
        } else {
          throw error;
        }
      }
    }
    chunks.push(valueHead);
    encodedValue = encodedValue.slice(encodedChunkHead.length);
  }
  return chunks.map((chunk, i) => ({ name: `${key}.${i}`, value: chunk }));
}

const env = {
  ...loadEnv(path.join(root, "frontend", ".env")),
  ...loadEnv(path.join(root, "backend", ".env")),
};

const supabaseUrl = env.SUPABASE_URL || env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = env.SUPABASE_ANON_KEY || env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const serviceKey = env.SUPABASE_SERVICE_ROLE_KEY;
if (!supabaseUrl || !anonKey || !serviceKey) {
  throw new Error("missing supabase env");
}

const projectRef = new URL(supabaseUrl).hostname.split(".")[0];
const cookieName = `sb-${projectRef}-auth-token`;

async function gotrue(pathname, { key, body, method = "POST" }) {
  const headers = {
    apikey: key,
    Authorization: `Bearer ${key}`,
  };
  if (body) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(`${supabaseUrl}/auth/v1${pathname}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const json = await res.json();
  if (!res.ok) {
    throw new Error(json.msg || json.message || json.error_description || JSON.stringify(json));
  }
  return json;
}

const userWrap = await gotrue(`/admin/users/${USER_ID}`, { key: serviceKey, method: "GET" });
const email = userWrap.user?.email || userWrap.email;
if (!email) {
  throw new Error("user email missing");
}

const linkData = await gotrue("/admin/generate_link", {
  key: serviceKey,
  body: { type: "magiclink", email },
});
const hashed = linkData.hashed_token || linkData.properties?.hashed_token;
if (!hashed) {
  throw new Error("hashed_token missing");
}

const verified = await gotrue("/verify", {
  key: anonKey,
  body: { type: "email", token_hash: hashed },
});
const session = verified.session || verified;
if (!session.access_token || !session.refresh_token || !session.user) {
  throw new Error("verify response missing session fields");
}
const expiresIn = session.expires_in || 3600;
const sessionValue = JSON.stringify({
  access_token: session.access_token,
  refresh_token: session.refresh_token,
  expires_at: session.expires_at || Math.floor(Date.now() / 1000) + expiresIn,
  expires_in: expiresIn,
  token_type: session.token_type || "bearer",
  user: session.user,
});

fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
await context.addCookies(
  createChunks(cookieName, sessionValue).map((chunk) => ({
    name: chunk.name,
    value: chunk.value,
    domain: "localhost",
    path: "/",
    sameSite: "Lax",
    httpOnly: false,
    secure: false,
  })),
);

const page = await context.newPage();
page.setDefaultTimeout(90_000);

async function shot(name, waitMs = 1800) {
  await page.waitForTimeout(waitMs);
  await page.screenshot({ path: path.join(outDir, name), fullPage: false });
  console.log("saved", name, page.url());
}

await page.goto(`${BASE}/subjects`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2000);
if (page.url().includes("/login")) {
  throw new Error("session cookie rejected; still on login");
}
await shot("03-subjects.png", 800);

await page.goto(`${BASE}/subjects/${SUBJECT_ID}/documents`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);
await shot("04-documents.png", 500);

await page.goto(`${BASE}/subjects/${SUBJECT_ID}/chat`, { waitUntil: "domcontentloaded" });
await page.getByText("Ajustes", { exact: true }).waitFor({ timeout: 30_000 });
await page.waitForTimeout(2000);

const threadBtn = page.locator("aside ul button").first();
if (await threadBtn.count()) {
  await threadBtn.click();
  await page.waitForTimeout(3000);
}

try {
  const citations = page.locator("ol button");
  if ((await citations.count()) === 0) {
    const input = page.locator("form input").last();
    await input.waitFor({ timeout: 20_000 });
    await input.fill("¿Qué es el modelo de negocio según el material?");
    await input.press("Enter");
    await citations.first().waitFor({ timeout: 90_000 }).catch(() => {});
  }
  if ((await citations.count()) > 0) {
    await citations.first().click();
    await page.waitForTimeout(800);
  }
} catch (err) {
  console.log("chat flow skipped:", err instanceof Error ? err.message : err);
}
await shot("05-chat.png", 400);
await page.keyboard.press("Escape").catch(() => {});

await page.goto(`${BASE}/subjects/${SUBJECT_ID}/quiz`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(3500);
await shot("06-quiz.png", 500);

await page.goto(`${BASE}/subjects/${SUBJECT_ID}/flashcards`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(3500);
await shot("07-flashcards.png", 500);

await page.goto(`${BASE}/subjects/${SUBJECT_ID}/planner`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);
await shot("08-planner.png", 400);

await browser.close();
console.log("done");
