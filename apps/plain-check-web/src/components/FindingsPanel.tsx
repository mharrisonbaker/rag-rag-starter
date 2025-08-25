
import React from 'react'
import FindingItem, { Finding } from './FindingItem'

import React from 'react'
import FindingItem, { Finding } from './FindingItem'
import { FaClipboardList } from 'react-icons/fa'

export default function FindingsPanel({ findings }: { findings: Finding[] }) {
  return (
    <div className="findings-panel">
      <h2 className="findings-header">
        <FaClipboardList style={{ marginRight: '0.5rem' }} />
        Analysis
      </h2>
      {findings.length === 0 && <p>No analysis yet. Start typing or paste content.</p>}
      {findings.length > 0 && (
        <div className="findings-list">
          <FindingItem f={findings[0]} />
        </div>
      )}
    </div>
  )
}

