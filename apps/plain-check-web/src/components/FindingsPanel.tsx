
import React from 'react'
import FindingItem, { Finding } from './FindingItem'

export default function FindingsPanel({ findings }: { findings: Finding[] }) {
  return (
    <div>
      <h2>Analysis</h2>
      {findings.length === 0 && <p>No analysis yet. Start typing or paste content.</p>}
      {findings.length > 0 && <FindingItem f={findings[0]} />}
    </div>
  )
}

