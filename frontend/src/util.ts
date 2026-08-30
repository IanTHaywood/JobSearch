export const COLUMN_CHAR_LIMIT = 200

export function truncate(value: unknown, limit = COLUMN_CHAR_LIMIT): string {
  const text = typeof value === 'string' ? value : JSON.stringify(value)
  if (text === undefined) return ''
  return text.length > limit ? `${text.slice(0, limit)}…` : text
}
