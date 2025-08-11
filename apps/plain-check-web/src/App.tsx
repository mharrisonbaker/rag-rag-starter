
import React, { useState, useCallback } from 'react'
import Editor from './components/Editor'
import FindingsPanel from './components/FindingsPanel'
import Upload from './components/Upload'
import { useLocalRAG } from './hooks/useLocalRAG'
import { debounce } from 'lodash-es'

export default function App() {
  const [text, setText] = useState('')
  const { loading, findings, checkText } = useLocalRAG()

  const debouncedCheckText = useCallback(debounce(checkText, 500), [checkText])

  const handleTextChange = (newText: string) => {
    setText(newText)
    debouncedCheckText(newText)
  }

  return (
    <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, padding:16}}>
      <div>
        <h1>Plain Language Checker</h1>
        <p>Paste or upload your draft. All analysis runs locally.</p>
        <Upload onText={handleTextChange} />
        <Editor value={text} onChange={handleTextChange} />
        <div style={{ opacity: 0.7, marginTop: 8 }}>
          {loading && 'Checking...'}
        </div>

      </div>
      <FindingsPanel findings={findings} />
    </div>
  )
}

