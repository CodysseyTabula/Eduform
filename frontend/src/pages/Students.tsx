import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header, NameCard } from '../components';
import { getStudents, createStudent, type Student } from '../utils/api';
import { formatBirthDate } from '../utils/dateFormat';
import plusIcon from '../assets/images/plus.png';
import './Students.css';

const Students: React.FC = () => {
  const navigate = useNavigate();
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState('');
  
  // 모달 상태
  const [name, setName] = useState('');
  const [birth, setBirth] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [modalError, setModalError] = useState('');

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      setIsLoading(true);
      setError('');
      const data = await getStudents();
      setStudents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '학생 목록을 불러오는데 실패했습니다.');
      console.error('Error loading students:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalError('');

    if (!name.trim()) {
      setModalError('학생 이름을 입력해주세요.');
      return;
    }

    if (!birth) {
      setModalError('생년월일을 입력해주세요.');
      return;
    }

    setIsSaving(true);
    try {
      await createStudent({ name: name.trim(), birth });
      setName('');
      setBirth('');
      setIsModalOpen(false);
      // 학생 추가 후 목록 새로고침
      await loadStudents();
    } catch (err) {
      setModalError(err instanceof Error ? err.message : '학생 추가에 실패했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleModalClose = () => {
    if (!isSaving) {
      setName('');
      setBirth('');
      setModalError('');
      setIsModalOpen(false);
    }
  };

  const handleStudentClick = (studentId: string) => {
    navigate(`/students/${studentId}/iep-versions`);
  };

  return (
    <div className="students-page">
      <Header />
      
      <div className="students-content">
        <h1 className="students-title">학생 목록</h1>
        
        {error && (
          <div className="students-error">
            {error}
            <button onClick={loadStudents} className="retry-button">
              다시 시도
            </button>
          </div>
        )}

        {isLoading ? (
          <div className="students-loading">로딩 중...</div>
        ) : (
          <div className="students-grid">
            {students.map((student) => (
              <NameCard
                key={student.id}
                title={student.name}
                description={formatBirthDate(student.birth)}
                onClick={() => handleStudentClick(student.id)}
              />
            ))}
            <div 
              className="add-student-button"
              onClick={() => setIsModalOpen(true)}
            >
              <img src={plusIcon} alt="추가" className="add-student-icon" />
              <p className="add-student-text">새 학생 추가하기</p>
            </div>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="modal-overlay" onClick={handleModalClose}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">새 학생 추가</h2>
              <button className="modal-close" onClick={handleModalClose} disabled={isSaving}>
                ×
              </button>
            </div>
            
            <form onSubmit={handleAddStudent} className="modal-form">
              <div className="form-group">
                <label htmlFor="student-name" className="form-label">
                  학생 이름
                </label>
                <input
                  id="student-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="form-input"
                  placeholder="학생 이름을 입력하세요"
                  disabled={isSaving}
                  maxLength={10}
                />
              </div>

              <div className="form-group">
                <label htmlFor="student-birth" className="form-label">
                  생년월일
                </label>
                <input
                  id="student-birth"
                  type="date"
                  value={birth}
                  onChange={(e) => setBirth(e.target.value)}
                  className="form-input"
                  disabled={isSaving}
                />
              </div>

              {modalError && <div className="form-error">{modalError}</div>}

              <div className="modal-actions">
                <button
                  type="button"
                  className="modal-button cancel"
                  onClick={handleModalClose}
                  disabled={isSaving}
                >
                  취소
                </button>
                <button
                  type="submit"
                  className="modal-button submit"
                  disabled={isSaving}
                >
                  {isSaving ? '저장 중...' : '저장'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Students;

