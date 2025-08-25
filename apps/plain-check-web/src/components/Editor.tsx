import React from 'react'
import React from 'react'

export default function Editor({ value, onChange }: { value: string; onChange: (s: string) => void }) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder='Paste your document here…'
      className="editor-textarea"
    />
  )
}
