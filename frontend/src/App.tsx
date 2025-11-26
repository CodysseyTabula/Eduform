import { Routes, Route, Navigate } from 'react-router-dom'
import Students from './pages/Students'
import IEPList from './pages/IEPList'
import Syllabus from './pages/Syllabus'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/students" replace />} />
      <Route path="/students" element={<Students />} />
      <Route path="/students/:studentId/iep-versions" element={<IEPList />} />
      <Route path="/students/:studentId/iep-versions/:iepVersionId/syllabus" element={<Syllabus />} />
    </Routes>
  )
}

export default App
