import React from 'react'
import FindingItem, { Finding } from './FindingItem'
export default function FindingsPanel({ findings }: { findings: Finding[] }) {
  return (
    <div>
      <h2>Findings</h2>
      {findings.length === 0 && <div>No issues found yet. Start typing or paste content.</div>}
      {findings.map((f, i) => <FindingItem key={i} f={f} />)}
    </div>
  )
}
