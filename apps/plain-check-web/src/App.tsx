import React, { useState } from 'react'
import Editor from './components/Editor'
import FindingsPanel from './components/FindingsPanel'
import Upload from './components/Upload'
import { useLocalRAG } from './hooks/useLocalRAG'

export default function App() {
  const [text, setText] = useState('')
  const { loading, search, indexInfo } = useLocalRAG()
  const findings = search(text)
  return (
    <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, padding:16}}>
      <div>
        <h1>Plain Language Checker</h1>
        <p>Paste or upload your draft. All analysis runs locally.</p>
        <Upload onText={setText} />
        <Editor value={text} onChange={setText} />
        <div style={{opacity:0.7, marginTop:8}}>
          {loading ? 'Loading guidelinesâ€¦' : Guidelines loaded:  chunks}
        </div>
      </div>
      <FindingsPanel findings={findings} />
    </div>
  )
}
