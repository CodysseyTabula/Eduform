import { Routes, Route, Navigate } from 'react-router-dom'
import Students from './pages/Students'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/students" replace />} />
      <Route path="/students" element={<Students />} />
      {/* 나중에 추가될 다른 페이지들 */}
    </Routes>
  )
}

export default App
