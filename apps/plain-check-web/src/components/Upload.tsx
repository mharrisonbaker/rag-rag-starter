import React, { useRef } from 'react'
export default function Upload({ onText }: { onText: (s: string) => void }) {
  const ref = useRef<HTMLInputElement>(null)
  return (
    <div style={{marginBottom:8}}>
      <input ref={ref} type='file' accept='.txt' onChange={async (e) => {
        const f = e.target.files?.[0]; if (!f) return
        const text = await f.text(); onText(text)
      }} />
    </div>
  )
}
