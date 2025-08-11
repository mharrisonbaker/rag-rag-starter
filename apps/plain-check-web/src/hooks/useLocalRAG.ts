
import { useState } from 'react'
import type { Finding } from '../components/FindingItem'

export function useLocalRAG() {
  const [loading, setLoading] = useState(false)
  const [findings, setFindings] = useState<Finding[]>([])

  async function checkText(text: string) {
    if (!text) {
      setFindings([])
      return
    }
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })
      const data = await response.json()
      setFindings(data.findings)
    } catch (error) {
      console.error("Error checking text:", error)
      // Handle error state here, e.g., show a message to the user
    } finally {
      setLoading(false)
    }
  }

  return { loading, findings, checkText }
}

