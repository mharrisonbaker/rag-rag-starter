import React from 'react'
export type Finding = {
  ruleId: string
  title: string
  message: string
  severity: 'info' | 'warn' | 'error'
  suggestion?: string
  refs: { page_start: number; page_end: number }[]
}
export default function FindingItem({ f }: { f: Finding }) {
  return (
    <div style={{border:'1px solid #ddd', borderRadius:8, padding:8, marginBottom:8}}>
      <div style={{fontWeight:600}}>{f.title}</div>
      <div style={{opacity:0.85}}>{f.message}</div>
      {f.suggestion && (
        <div style={{marginTop: 8, padding: 8, backgroundColor: '#f5f5f5', borderRadius: 4}}>
          <strong>Suggestion:</strong>
          <p style={{whiteSpace: 'pre-wrap'}}>{f.suggestion}</p>
        </div>
      )}
      {f.refs && f.refs.length > 0 && (
        <div style={{fontSize:12, opacity:0.7, marginTop:4}}>
          Source: Federal Plain Language Guidelines (pp. {f.refs[0].page_start}–{f.refs[0].page_end})
        </div>
      )}
    </div>
  )
}