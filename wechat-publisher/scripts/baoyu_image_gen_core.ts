import path from "node:path";
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

export type Provider = "openai" | "gemini-proxy" | "ideogram" | "evolink";
export type Quality = "normal" | "2k";

export type CliArgs = {
  prompt: string | null;
  promptFiles: string[];
  imagePath: string | null;
  provider: Provider | null;
  model: string | null;
  aspectRatio: string | null;
  size: string | null;
  quality: Quality;
  referenceImages: string[];
  n: number;
  json: boolean;
  help: boolean;
};

type OpenAIImageResult = {
  data?: Array<{ url?: string; b64_json?: string }>;
};

type ChatCompletionResult = {
  choices?: Array<{
    message?: {
      content?: unknown;
      images?: Array<{ url?: string; b64_json?: string; b64?: string }>;
      image_url?: { url?: string };
    };
  }>;
  candidates?: Array<{
    content?: {
      parts?: Array<{
        inlineData?: { data?: string };
        text?: string;
      }>;
    };
  }>;
};

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(SCRIPT_DIR, "..");
const CONFIG_PATH = path.join(SKILL_ROOT, "config.yaml");
const CONFIG_EXPORT_KEYS = [
  "WECHAT_PUBLISHER_IMAGE_GENERATOR",
  "OPENAI_API_KEY",
  "OPENAI_BASE_URL",
  "OPENAI_IMAGE_MODEL",
  "GEMINI_PROXY_API_KEY",
  "GEMINI_PROXY_BASE_URL",
  "GEMINI_PROXY_IMAGE_MODEL",
  "GEMINI_WEB_DATA_DIR",
  "GEMINI_WEB_COOKIE_PATH",
  "GEMINI_WEB_CHROME_PROFILE_DIR",
  "GEMINI_WEB_CHROME_PATH",
  "EVOLINK_API_KEY",
  "EVOLINK_BASE_URL",
  "EVOLINK_IMAGE_MODEL",
  "IDEOGRAM_API_KEY",
  "WECHATSYNC_MCP_TOKEN",
] as const;

function hasConfiguredProviderEnv(): boolean {
  return Boolean(
    process.env.EVOLINK_API_KEY ||
    process.env.IDEOGRAM_API_KEY ||
    process.env.GEMINI_PROXY_API_KEY ||
    process.env.OPENAI_API_KEY
  );
}

function hasCanonicalConfigFile(): boolean {
  return existsSync(CONFIG_PATH);
}

function hasLoadedProviderEnv(
  loaded: Partial<Record<(typeof CONFIG_EXPORT_KEYS)[number], string | null>>
): boolean {
  return Boolean(loaded.OPENAI_API_KEY || loaded.GEMINI_PROXY_API_KEY || loaded.IDEOGRAM_API_KEY || loaded.EVOLINK_API_KEY);
}

export async function loadEnv(): Promise<void> {
  if (typeof Bun === "undefined") return;

  const python = `
import json
import os
import sys
from pathlib import Path

keys = ${JSON.stringify([...CONFIG_EXPORT_KEYS])}
sys.path.insert(0, str(Path.cwd() / "scripts"))

for key in keys:
    os.environ.pop(key, None)

import config  # noqa: E402

config.load_env()
print(json.dumps({key: os.environ.get(key) for key in keys}))
`.trim();

  const result = Bun.spawnSync({
    cmd: ["python3", "-c", python],
    cwd: SKILL_ROOT,
    env: process.env,
    stdout: "pipe",
    stderr: "pipe",
  });

  if (result.exitCode !== 0) {
    const stderr = Buffer.from(result.stderr).toString("utf8").trim();
    if (!hasCanonicalConfigFile() && hasConfiguredProviderEnv()) return;
    throw new Error(stderr || "Failed to load config.yaml via scripts/config.py");
  }

  const stderr = Buffer.from(result.stderr).toString("utf8").trim();
  if (stderr) {
    throw new Error(stderr);
  }

  const output = Buffer.from(result.stdout).toString("utf8").trim();
  if (!output) {
    if (!hasCanonicalConfigFile() && hasConfiguredProviderEnv()) return;
    throw new Error("config.yaml did not export any image provider settings");
  }

  try {
    const loaded = JSON.parse(output) as Partial<Record<(typeof CONFIG_EXPORT_KEYS)[number], string | null>>;
    const hasCanonicalConfig = hasCanonicalConfigFile();
    if (hasCanonicalConfig && !hasLoadedProviderEnv(loaded)) {
      throw new Error(
        "config.yaml does not configure OPENAI_API_KEY, IDEOGRAM_API_KEY, or EVOLINK_API_KEY"
      );
    }

    for (const key of CONFIG_EXPORT_KEYS) {
      const value = loaded[key];
      if (hasCanonicalConfig) {
        if (value) process.env[key] = value;
        else delete process.env[key];
        continue;
      }
      if (value && !process.env[key]) {
        process.env[key] = value;
      }
    }
    return;
  }
  catch (error) {
    if (!hasCanonicalConfigFile() && hasConfiguredProviderEnv()) return;
    throw new Error(
      error instanceof Error
        ? `Failed to parse config exports: ${error.message}`
        : "Failed to parse config exports"
    );
  }
}

export function detectProvider(args: CliArgs): Provider {
  if (args.provider) return args.provider;
  if (process.env.EVOLINK_API_KEY) return "evolink";
  if (process.env.IDEOGRAM_API_KEY) return "ideogram";
  if (process.env.GEMINI_PROXY_API_KEY) return "gemini-proxy";
  if (process.env.OPENAI_API_KEY) return "openai";
  throw new Error(
    "No image provider configured. Set EVOLINK_API_KEY, IDEOGRAM_API_KEY, GEMINI_PROXY_API_KEY, or OPENAI_API_KEY."
  );
}

export function getDefaultModel(provider: Provider): string {
  if (provider === "evolink") return process.env.EVOLINK_IMAGE_MODEL || "z-image-turbo";
  if (provider === "ideogram") return "V_4_TURBO";
  if (provider === "gemini-proxy") {
    return process.env.GEMINI_PROXY_IMAGE_MODEL || "gemini-2.5-flash";
  }
  return process.env.OPENAI_IMAGE_MODEL || "gpt-image-1";
}

export async function buildPrompt(args: CliArgs): Promise<string> {
  if (args.prompt) return args.prompt;
  if (args.promptFiles.length > 0) {
    const parts: string[] = [];
    for (const file of args.promptFiles) {
      parts.push(await readFile(file, "utf8"));
    }
    return parts.join("\n\n").trim();
  }

  if (!process.stdin.isTTY) {
    try {
      const stdin = await Bun.stdin.text();
      if (stdin.trim()) return stdin.trim();
    } catch {}
  }

  throw new Error("Prompt is required.");
}

export function normalizeOutputImagePath(filePath: string): string {
  const full = path.resolve(filePath);
  return path.extname(full) ? full : `${full}.png`;
}

export async function generateImage(
  provider: Provider,
  model: string,
  prompt: string,
  args: CliArgs
): Promise<Uint8Array> {
  if (provider === "evolink") {
    return generateWithEvolink(prompt, model, args);
  }
  if (provider === "ideogram") {
    return generateWithIdeogram(prompt, model, args);
  }
  if (provider === "gemini-proxy") {
    return generateWithGeminiProxy(prompt, model, args);
  }
  return generateWithOpenAI(prompt, model, args);
}

async function generateWithOpenAI(
  prompt: string,
  model: string,
  args: CliArgs
): Promise<Uint8Array> {
  const baseURL = (process.env.OPENAI_BASE_URL || "https://api.openai.com/v1").replace(/\/$/, "");
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY is required");

  const body: Record<string, unknown> = {
    model,
    prompt: applyPromptHints(prompt, args),
    size: args.size || getOpenAISize(args.aspectRatio, args.quality),
    n: args.n,
  };

  const res = await fetch(`${baseURL}/images/generations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`OpenAI image API error: ${await res.text()}`);
  }

  return extractImageBytes(await res.json() as OpenAIImageResult);
}

// ──────────────────────────────────────────────
// Evolink (async polling)
// ──────────────────────────────────────────────

type EvolinkTaskResponse = {
  id?: string;
  status?: string;
  created?: number;
  progress?: number;
  result_data?: Array<{ url?: string }>;
  results?: string[];
};

const EVOLINK_POLL_INTERVAL_MS = 2000;
const EVOLINK_MAX_POLL_SECONDS = 120;

async function generateWithEvolink(
  prompt: string,
  model: string,
  args: CliArgs
): Promise<Uint8Array> {
  const baseURL = (process.env.EVOLINK_BASE_URL || "https://api.evolink.ai/v1").replace(/\/$/, "");
  const apiKey = process.env.EVOLINK_API_KEY;
  if (!apiKey) throw new Error("EVOLINK_API_KEY is required");

  // Step 1: Submit the generation task
  const size = resolveEvolinkSize(args.aspectRatio, args.size);

  const body: Record<string, unknown> = {
    model,
    prompt: applyPromptHints(prompt, args),
  };
  if (size) body.size = size;

  const submitRes = await fetch(`${baseURL}/images/generations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!submitRes.ok) {
    throw new Error(`Evolink submit error: ${await submitRes.text()}`);
  }

  const taskJson = await submitRes.json() as EvolinkTaskResponse;
  const taskId = taskJson.id;
  if (!taskId) {
    throw new Error(`Evolink did not return a task ID: ${JSON.stringify(taskJson)}`);
  }

  // Step 2: Poll until succeeded or timeout
  const deadline = Date.now() + EVOLINK_MAX_POLL_SECONDS * 1000;
  let lastStatus = taskJson.status || "pending";

  while (Date.now() < deadline) {
    // Wait before polling (skip wait on first attempt if status is already done)
    if (lastStatus !== "completed" && lastStatus !== "succeeded" && lastStatus !== "failed") {
      await new Promise((r) => setTimeout(r, EVOLINK_POLL_INTERVAL_MS));
    }

    const pollRes = await fetch(`${baseURL}/tasks/${taskId}`, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
    });

    if (!pollRes.ok) {
      throw new Error(`Evolink poll error: ${await pollRes.text()}`);
    }

    const pollJson = await pollRes.json() as EvolinkTaskResponse;
    lastStatus = pollJson.status || "unknown";

    if (lastStatus === "completed" || lastStatus === "succeeded") {
      // Try result_data first, then results (plain URL array)
      let imageUrl: string | undefined;
      if (pollJson.result_data && pollJson.result_data.length > 0) {
        imageUrl = pollJson.result_data[0]?.url;
      }
      if (!imageUrl && pollJson.results && pollJson.results.length > 0) {
        imageUrl = pollJson.results[0];
      }
      if (!imageUrl) {
        throw new Error(`Evolink task succeeded but has no output URL: ${JSON.stringify(pollJson)}`);
      }

      // Download the image from the output URL
      const imgRes = await fetch(imageUrl);
      if (!imgRes.ok) {
        throw new Error(`Failed to download Evolink image: ${imgRes.statusText}`);
      }
      return new Uint8Array(await imgRes.arrayBuffer());
    }

    if (lastStatus === "failed") {
      throw new Error(`Evolink task failed: ${JSON.stringify(pollJson)}`);
    }

    // Also break early if progress reached 100 but status isn't updated yet
    if (pollJson.progress === 100 && lastStatus !== "completed" && lastStatus !== "succeeded") {
      // Continue polling — next response should have completed status
    }
  }

  throw new Error(`Evolink task timed out after ${EVOLINK_MAX_POLL_SECONDS}s (last status: ${lastStatus})`);
}

function resolveEvolinkSize(aspectRatio: string | null, explicitSize: string | null): string | null {
  if (explicitSize) return explicitSize;
  if (!aspectRatio) return null; // Evolink defaults to 1:1
  return aspectRatio; // Evolink accepts aspect ratio strings like "16:9"
}

// ──────────────────────────────────────────────
// Ideogram
// ──────────────────────────────────────────────

type IdeogramImageObject = {
  url?: string;
  resolution?: string;
  is_image_safe?: boolean;
  seed?: number;
};

type IdeogramResponse = {
  created?: string;
  data?: IdeogramImageObject[];
  response_type?: string;
};

// Map aspect ratio to the closest Ideogram 4.0 resolution.
// The ratios below are approximate; we pick the best match for each common
// aspect ratio, falling back to square.
function resolveIdeogramResolution(aspectRatio: string | null, quality: Quality): string {
  const highRes = quality === "2k";
  if (!aspectRatio) return highRes ? "2048x2048" : "1440x1440";

  const map: Record<string, string> = {
    "1:1": highRes ? "2048x2048" : "1440x1440",
    "16:9": highRes ? "2560x1440" : "2560x1440",
    "9:16": highRes ? "1440x2560" : "1440x2560",
    "4:3": "1728x2304",
    "3:4": "2304x1728",
    "3:2": "2496x1664",
    "2:3": "1664x2496",
    "2:1": "2880x1440",
    "1:2": "1440x2880",
    "5:4": "2240x1792",
    "4:5": "1792x2240",
    "8:5": "2560x1600",
    "5:8": "1600x2560",
  };

  return map[aspectRatio] || "1440x1440";
}

// Map our quality to Ideogram rendering_speed
function ideogramRenderingSpeed(quality: Quality): string {
  if (quality === "2k") return "DEFAULT";
  return "TURBO"; // cheapest: $0.03/image
}

async function generateWithIdeogram(
  prompt: string,
  model: string,
  args: CliArgs
): Promise<Uint8Array> {
  const apiKey = process.env.IDEOGRAM_API_KEY;
  if (!apiKey) throw new Error("IDEOGRAM_API_KEY is required");

  const resolution = args.size || resolveIdeogramResolution(args.aspectRatio, args.quality);

  // Build multipart form-data
  const formData = new FormData();
  formData.append("text_prompt", applyPromptHints(prompt, args));
  formData.append("resolution", resolution);
  formData.append("rendering_speed", ideogramRenderingSpeed(args.quality));

  const res = await fetch("https://api.ideogram.ai/v1/ideogram-v4/generate", {
    method: "POST",
    headers: {
      "Api-Key": apiKey,
    },
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Ideogram API error: ${await res.text()}`);
  }

  const json = await res.json() as IdeogramResponse;
  const data = json.data;
  if (!data || data.length === 0 || !data[0]?.url) {
    throw new Error("Ideogram returned no image URL");
  }

  // Download the ephemeral URL immediately
  const imgRes = await fetch(data[0].url);
  if (!imgRes.ok) {
    throw new Error(`Failed to download Ideogram image: ${imgRes.statusText}`);
  }

  return new Uint8Array(await imgRes.arrayBuffer());
}

async function generateWithGeminiProxy(
  prompt: string,
  model: string,
  args: CliArgs
): Promise<Uint8Array> {
  const baseURL = normalizeGeminiProxyBaseUrl(process.env.GEMINI_PROXY_BASE_URL);
  const apiKey = process.env.GEMINI_PROXY_API_KEY;
  if (!baseURL) throw new Error("GEMINI_PROXY_BASE_URL is required");
  if (!apiKey) throw new Error("GEMINI_PROXY_API_KEY is required");

  const content: Array<Record<string, unknown>> = [];
  for (const file of args.referenceImages) {
    const { dataUrl } = await readImageAsDataUrl(file);
    content.push({ type: "image_url", image_url: { url: dataUrl } });
  }
  content.push({
    type: "text",
    text: buildGeminiProxyPrompt(prompt, args),
  });

  const body = {
    model,
    messages: [{ role: "user", content }],
  };

  const res = await fetch(`${baseURL}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`Gemini proxy API error: ${await res.text()}`);
  }

  return extractImageBytes(await res.json() as ChatCompletionResult);
}

function normalizeGeminiProxyBaseUrl(raw: string | undefined): string | null {
  const trimmed = raw?.trim();
  if (!trimmed) return null;
  const withoutSlash = trimmed.replace(/\/+$/, "");
  return withoutSlash.endsWith("/v1") ? withoutSlash : `${withoutSlash}/v1`;
}

function buildGeminiProxyPrompt(prompt: string, args: CliArgs): string {
  const parts = [
    "Generate exactly one image.",
    "Return image data directly if the proxy supports it.",
    "Preferred response order: base64 image, image URL, then nothing else.",
    applyPromptHints(prompt, args),
  ];
  return parts.join("\n");
}

function applyPromptHints(prompt: string, args: CliArgs): string {
  let result = prompt.trim();
  if (args.aspectRatio) result += `\nAspect ratio: ${args.aspectRatio}.`;
  if (args.quality === "2k") result += "\nHigh resolution target: 2048px.";
  if (args.size) result += `\nTarget size: ${args.size}.`;
  return result;
}

function getOpenAISize(aspectRatio: string | null, quality: Quality): string {
  const base = quality === "2k" ? 2048 : 1024;
  if (!aspectRatio) return `${base}x${base}`;
  if (aspectRatio === "16:9") return quality === "2k" ? "2048x1024" : "1792x1024";
  if (aspectRatio === "9:16") return quality === "2k" ? "1024x2048" : "1024x1792";
  return `${base}x${base}`;
}

async function readImageAsDataUrl(filePath: string): Promise<{ dataUrl: string }> {
  const bytes = await readFile(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime =
    ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" :
    ext === ".webp" ? "image/webp" :
    ext === ".gif" ? "image/gif" :
    "image/png";
  return { dataUrl: `data:${mime};base64,${bytes.toString("base64")}` };
}

function extractImageBytes(payload: unknown): Promise<Uint8Array> {
  const direct = extractInlineImage(payload);
  if (direct) return Promise.resolve(direct);

  const url = extractImageUrl(payload);
  if (url) return downloadImage(url);

  throw new Error("Cannot extract image data from response.");
}

function extractInlineImage(payload: unknown): Uint8Array | null {
  const dataUrl = findString(payload, (value) => value.startsWith("data:image/"));
  const base64Value = dataUrl ?? findString(payload, (value) => isLikelyImageBase64(value));
  if (!base64Value) return null;
  const raw = base64Value.startsWith("data:image/")
    ? base64Value.slice(base64Value.indexOf(",") + 1)
    : base64Value;
  return Uint8Array.from(Buffer.from(raw, "base64"));
}

function extractImageUrl(payload: unknown): string | null {
  return findString(payload, (value) =>
    value.startsWith("https://") &&
    (value.includes(".png") || value.includes(".jpg") || value.includes(".jpeg") || value.includes(".webp") || value.includes("image"))
  );
}

function findString(value: unknown, match: (text: string) => boolean): string | null {
  if (typeof value === "string") return match(value) ? value : null;
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = findString(item, match);
      if (found) return found;
    }
    return null;
  }
  if (value && typeof value === "object") {
    for (const child of Object.values(value as Record<string, unknown>)) {
      const found = findString(child, match);
      if (found) return found;
    }
  }
  return null;
}

function isLikelyImageBase64(value: string): boolean {
  if (value.length < 256) return false;
  if (value.length % 4 !== 0) return false;
  if (!/^[A-Za-z0-9+/=\r\n]+$/.test(value)) return false;
  const prefix = Buffer.from(value.slice(0, 64), "base64");
  return (
    prefix.subarray(0, 3).equals(Buffer.from([0xff, 0xd8, 0xff])) ||
    prefix.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])) ||
    prefix.subarray(0, 4).toString("ascii") === "RIFF"
  );
}

async function downloadImage(url: string): Promise<Uint8Array> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to download image from ${url}`);
  }
  return new Uint8Array(await res.arrayBuffer());
}
