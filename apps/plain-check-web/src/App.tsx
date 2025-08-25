
import React, { useState, useCallback, useEffect } from 'react'
import Editor from './components/Editor'
import FindingsPanel from './components/FindingsPanel'
import Upload from './components/Upload'
import ThemeToggle from './components/ThemeToggle'
import { useLocalRAG } from './hooks/useLocalRAG'
import { debounce } from 'lodash-es'

export default function App() {
  const [text, setText] = useState('')
  const { loading, findings, checkText } = useLocalRAG()
  const [theme, setTheme] = useState('light')

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const debouncedCheckText = useCallback(debounce(checkText, 500), [checkText])

  const handleTextChange = (newText: string) => {
    setText(newText)
    debouncedCheckText(newText)
  }

  return (
    <main className="container">
      <header style={{ textAlign: 'center', margin: '2rem 0', position: 'relative' }}>
        <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
        <h1>Plain Language Checker</h1>
        <p>Paste or upload your draft to get suggestions based on the Federal Plain Language Guidelines.</p>
        <p>
          <a href="https://www.opm.gov/policy-data-oversight/latest-memos/" target="_blank" rel="noopener noreferrer">
            View sample memos
          </a>
        </p>
      </header>
      <div className="grid-container">
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

