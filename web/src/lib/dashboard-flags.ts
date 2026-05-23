declare global {
  interface Window {
    /** Set true by the server only for `shaggy dashboard --tui` (or SHAGGY_DASHBOARD_TUI=1). */
    __SHAGGY_DASHBOARD_EMBEDDED_CHAT__?: boolean;
    /** @deprecated Older injected name; treated as on when true. */
    __SHAGGY_DASHBOARD_TUI__?: boolean;
  }
}

/** True only when the dashboard was started with embedded TUI Chat (`shaggy dashboard --tui`). */
export function isDashboardEmbeddedChatEnabled(): boolean {
  if (typeof window === "undefined") return false;
  if (window.__SHAGGY_DASHBOARD_EMBEDDED_CHAT__ === true) return true;
  return window.__SHAGGY_DASHBOARD_TUI__ === true;
}
