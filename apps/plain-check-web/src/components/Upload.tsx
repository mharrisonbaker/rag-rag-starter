import React from 'react'

export default function Upload({ onText }: { onText: (s: string) => void }) {
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const text = await file.text()
    onText(text)
  }

  return (
    <div style={{ marginBottom: '1rem' }}>
      <label htmlFor="file">Upload a .txt file:</label>
      <input 
        type="file" 
        id="file"
        name="file"
        accept=".txt" 
        onChange={handleFileChange} 
      />
    </div>
  )
}
