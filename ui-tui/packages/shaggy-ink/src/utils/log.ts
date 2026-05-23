export function logError(error: unknown): void {
  if (!process.env.SHAGGY_INK_DEBUG_ERRORS) {
    return
  }

  console.error(error)
}
