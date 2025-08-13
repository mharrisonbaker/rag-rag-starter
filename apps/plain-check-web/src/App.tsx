
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
    <main className="container">
      <header style={{ textAlign: 'center', margin: '2rem 0' }}>
        <h1>Plain Language Checker</h1>
        <p>Paste or upload your draft to get suggestions based on the Federal Plain Language Guidelines.</p>
      </header>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: '2rem'}}>
        <section>
          <Upload onText={handleTextChange} />
          <Editor value={text} onChange={handleTextChange} />
          {loading && <div aria-busy="true">Checking...</div>}
        </section>
        <section>
          <FindingsPanel findings={findings} />
        </section>
      </div>
    </main>
  )
}

