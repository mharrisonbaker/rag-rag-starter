
import React from 'react'

export type Finding = {
  ruleId: string
  title: string
  message: string
  severity: 'info' | 'warn' | 'error'
}

export default function FindingItem({ f }: { f: Finding }) {
  return (
    <article>
      <header>
        <strong>{f.title}</strong>
      </header>
      <p style={{whiteSpace: 'pre-wrap'}}>{f.message}</p>
    </article>
  )
}
