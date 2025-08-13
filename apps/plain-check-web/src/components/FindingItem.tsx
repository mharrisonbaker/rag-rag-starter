
import React from 'react'

export type Finding = {
  ruleId: string
  title: string
  message: string
  severity: 'info' | 'warn' | 'error'
  suggestion?: string
  trigger_text?: string
  refs: { page_start: number; page_end: number }[]
}

export default function FindingItem({ f }: { f: Finding }) {
  return (
    <article style={{marginBottom: '1rem'}}>
      <header>
        <strong style={f.severity === 'warn' ? {color: 'orange'} : {}}>{f.title}</strong>
      </header>
      <p>{f.message}</p>
      {f.trigger_text && (
        <details>
          <summary>View Source</summary>
          <p><em>"{f.trigger_text}"</em></p>
        </details>
      )}
      {f.suggestion && (
        <details>
          <summary>View Suggestion</summary>
          <p style={{whiteSpace: 'pre-wrap'}}>{f.suggestion}</p>
        </details>
      )}
      {f.refs && f.refs.length > 0 && (
        <footer>
          <small>Source: Federal Plain Language Guidelines (pp. {f.refs[0].page_start}–{f.refs[0].page_end})</small>
        </footer>
      )}
    </article>
  )
}
