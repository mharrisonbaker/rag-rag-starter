import type { Finding } from '../components/FindingItem'

type Chunk = { id: string; text: string; page_start: number; page_end: number }
type Index = { chunks: Chunk[]; num_chunks: number }

export function lint(text: string, index: Index): Finding[] {
  const findings: Finding[] = []

  // Long sentences
  const sentences = text.split(/(?<=[.!?])\s+/)
  const long = sentences.filter(s => s.split(/\s+/).length > 25)
  if (long.length) {
    const src = nearest(index, 'short sentences concise')
    findings.push({
      ruleId: 'sentence-length',
      title: 'Short sentences',
      message: String(long.length) + ' sentence(s) exceed ~25 words. Split and front-load the key point.',
      severity: 'warn',
      refs: src
    })
  }

  // Passive voice (naive)
  const passive = (text.match(/\b(is|are|was|were|been|be|being)\s+\w+ed\b/gi) || []).length
  if (passive > 3) {
    const src = nearest(index, 'active voice you we direct')
    findings.push({
      ruleId: 'active-voice',
      title: 'Use active voice',
      message: 'Detected several passive constructions. Prefer subject–verb–object with "you" where possible.',
      severity: 'warn',
      refs: src
    })
  }

  // Link text
  if (/click here|read more|learn more/i.test(text)) {
    const src = nearest(index, 'links link text descriptive')
    findings.push({
      ruleId: 'link-text',
      title: 'Make link text descriptive',
      message: 'Replace "click here/read more" with meaningful link text that names the target.',
      severity: 'info',
      refs: src
    })
  }

  // Jargon
  const jargon = /(utilize|facilitate|leverage|paradigm|robust|synergy)/i
  if (jargon.test(text)) {
    const src = nearest(index, 'plain words simple familiar')
    findings.push({
      ruleId: 'plain-words',
      title: 'Prefer plain words',
      message: 'Replace jargon with simple, familiar words.',
      severity: 'info',
      refs: src
    })
  }

  return findings
}

function nearest(index: Index, hint: string) {
  const lc = hint.toLowerCase().split(/\s+/)
  const scored = index.chunks
    .map(ch => {
      const t = ch.text.toLowerCase()
      const s = lc.reduce((acc, w) => acc + (t.includes(w) ? 1 : 0), 0)
      return { ch, s }
    })
    .sort((a, b) => b.s - a.s)
  return scored.slice(0, 1).map(({ ch }) => ({ page_start: ch.page_start, page_end: ch.page_end }))
}
