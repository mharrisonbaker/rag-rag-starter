
import React from 'react'

export type Finding = {
  ruleId: string
  title: string
  message: string
  severity: 'info' | 'warn' | 'error'
}

export default function FindingItem({ f }: { f: Finding }) {
  return (
    <article className={`finding-item severity-${f.severity} fade-in`}>
      <header className="finding-item-header">
        <strong>{f.title}</strong>
      </header>
      <p className="finding-item-message">{f.message}</p>
    </article>
  )
}
