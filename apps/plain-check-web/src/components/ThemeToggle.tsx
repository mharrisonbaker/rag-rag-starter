import React from 'react'
import { FaSun, FaMoon } from 'react-icons/fa'

export default function ThemeToggle({ theme, toggleTheme }: { theme: string; toggleTheme: () => void }) {
  return (
    <button onClick={toggleTheme} className="theme-toggle-button">
      {theme === 'light' ? <FaMoon /> : <FaSun />}
    </button>
  )
}