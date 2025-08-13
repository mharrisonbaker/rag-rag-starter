import React from 'react'
export default function Editor({ value, onChange }: { value: string; onChange: (s: string) => void }) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder='Paste your document here…'
      style={{ width:'100%', minHeight: '50vh', fontFamily:'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace' }}
    />
  )
}
