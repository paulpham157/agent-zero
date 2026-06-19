import { getModalStack, isModalOpen, openModal } from "/js/modals.js";

const MODAL_PATH = "/plugins/_whats_new/webui/whats-new.html";
const STORAGE_KEY = "a0_whats_new_seen_version";
const STARTUP_DELAY_MS = 1200;
const RETRY_DELAY_MS = 900;
const MAX_BUSY_RETRIES = 20;

let initialized = false;
let busyRetries = 0;
let openedForVersion = null;

function cleanPath(path = "") {
  return String(path || "").replace(/^\/+/, "");
}

function parseVersion(value) {
  const raw = String(value || "").trim();
  if (!raw || raw.toLowerCase() === "unknown") return null;

  const match = /(?:^|[\s(])v?(\d+)\.(\d+)(?:\.(\d+))?(?:\+(\d+))?/.exec(raw);
  if (!match) return null;

  return {
    raw,
    parts: [
      Number.parseInt(match[1], 10),
      Number.parseInt(match[2], 10),
      Number.parseInt(match[3] || "0", 10),
    ],
  };
}

function compareVersions(left, right) {
  if (!left || !right) return null;
  for (let index = 0; index < left.parts.length; index += 1) {
    if (left.parts[index] !== right.parts[index]) {
      return left.parts[index] - right.parts[index];
    }
  }
  return 0;
}

function currentVersion() {
  return parseVersion(globalThis.gitinfo?.version || "");
}

function storedSeenVersion() {
  try {
    const rawValue = globalThis.localStorage?.getItem(STORAGE_KEY) || "";
    if (!rawValue) return null;

    try {
      const parsed = JSON.parse(rawValue);
      return parseVersion(parsed?.version || parsed?.raw || rawValue);
    } catch {
      return parseVersion(rawValue);
    }
  } catch {
    return null;
  }
}

function shouldShowWhatsNew(version) {
  if (!version) return false;

  const seen = storedSeenVersion();
  if (!seen) return true;

  const comparison = compareVersions(version, seen);
  return comparison !== null && comparison > 0;
}

function markVersionSeen(version = currentVersion()) {
  if (!version) return;
  try {
    globalThis.localStorage?.setItem(
      STORAGE_KEY,
      JSON.stringify({
        version: version.raw,
        seenAt: new Date().toISOString(),
      }),
    );
  } catch {
    // localStorage may be unavailable in private or locked-down browser modes.
  }
}

function anotherModalIsOpen() {
  return getModalStack().length > 0 || Boolean(document.querySelector(".modal.show"));
}

function scheduleRetry() {
  if (busyRetries >= MAX_BUSY_RETRIES) return;
  busyRetries += 1;
  window.setTimeout(() => {
    maybeOpenWhatsNew();
  }, RETRY_DELAY_MS);
}

function maybeOpenWhatsNew() {
  const version = currentVersion();
  if (!shouldShowWhatsNew(version)) return;

  if (isModalOpen(MODAL_PATH)) return;
  if (anotherModalIsOpen()) {
    scheduleRetry();
    return;
  }

  openedForVersion = version;
  void openModal(MODAL_PATH);
}

function handleModalClosed(event) {
  const closedPath = event?.detail?.modalPath || "";
  if (cleanPath(closedPath) === cleanPath(MODAL_PATH)) {
    markVersionSeen(openedForVersion || currentVersion());
    openedForVersion = null;
    return;
  }

  window.setTimeout(() => {
    maybeOpenWhatsNew();
  }, RETRY_DELAY_MS);
}

export default function initWhatsNew() {
  if (initialized) return;
  initialized = true;

  document.addEventListener("modal-closed", handleModalClosed);

  window.setTimeout(() => {
    maybeOpenWhatsNew();
  }, STARTUP_DELAY_MS);
}
