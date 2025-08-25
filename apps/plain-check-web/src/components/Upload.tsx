import React from 'react'

import React from 'react'
import { FaUpload } from 'react-icons/fa'

export default function Upload({ onText }: { onText: (s: string) => void }) {
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const text = await file.text()
    onText(text)
  }

  return (
    <div className="upload-container">
      <label htmlFor="file" className="upload-button">
        <FaUpload style={{ marginRight: '0.5rem' }} />
        Choose File
      </label>
      <input
        type="file"
        id="file"
        name="file"
        accept=".txt"
        onChange={handleFileChange}
        className="upload-input"
      />
    </div>
  )
}
