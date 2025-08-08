export function bowBM25Score(query: string, text: string) {
  const q = query.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean)
  const t = text.toLowerCase()
  let score = 0
  for (const tok of q) {
    const re = new RegExp(\\b\\b, 'g')
    const matches = t.match(re)
    if (matches) score += Math.min(3, matches.length)
  }
  return score
}
