import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Header, Sidebar, Line, TextBox, Dropdown, CheckboxGroup, Button } from '../components';
import { 
  getIEPVersions, 
  getLatestIEP, 
  createIEPVersion, 
  getIEPFiles,
  createIEPFile,
  updateIEPFile,
  getIEPFileContent,
  downloadIEPDocx,
  type IEPVersion,
  type IEPFile
} from '../utils/api';
import { getStudents, type Student } from '../utils/api';
import penIcon from '../assets/images/pen.png';
import downloadIcon from '../assets/images/download.png';
import './IEPList.css';

interface IEPFormData {
  name: string;
  birth: string;
  grade: string;
  current_semester: string;
  iep_start_date: string;
  iep_end_date: string;
  guardian_opinion: string;
  cognitive_level: string;
  social_psych_level: string;
  motor_daily_level: string;
  vci_score: number;
  visual_spatial_score: number;
  fri_score: number;
  wmi_score: number;
  psi_score: number;
  fsiq_score: number;
  korean_performance_level: string;
  math_performance_level: string;
  korean_domain: string;
  math_domain: string;
}

const IEPList: React.FC = () => {
  const { studentId } = useParams<{ studentId: string }>();
  const navigate = useNavigate();
  
  const [student, setStudent] = useState<Student | null>(null);
  const [iepVersions, setIepVersions] = useState<IEPVersion[]>([]);
  const [currentIepId, setCurrentIepId] = useState<string | null>(null);
  const [currentIepFileId, setCurrentIepFileId] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // 모달 상태
  const [modalYear, setModalYear] = useState('');
  const [modalSemester, setModalSemester] = useState('');
  const [modalError, setModalError] = useState('');
  
  // 폼 데이터
  const [formData, setFormData] = useState<IEPFormData>({
    name: '',
    birth: '',
    grade: '',
    current_semester: '',
    iep_start_date: '',
    iep_end_date: '',
    guardian_opinion: '',
    cognitive_level: '',
    social_psych_level: '',
    motor_daily_level: '',
    vci_score: 0,
    visual_spatial_score: 0,
    fri_score: 0,
    wmi_score: 0,
    psi_score: 0,
    fsiq_score: 0,
    korean_performance_level: '',
    math_performance_level: '',
    korean_domain: '',
    math_domain: '',
  });
  
  // 교과목 선택
  const [subject1, setSubject1] = useState<string>('');
  const [subject2, setSubject2] = useState<string>('');
  const [koreanDomains, setKoreanDomains] = useState<string[]>([]);
  const [mathDomains, setMathDomains] = useState<string[]>([]);

  useEffect(() => {
    if (studentId) {
      loadData();
    }
  }, [studentId]);

  const loadData = async () => {
    if (!studentId) return;
    
    try {
      setIsLoading(true);
      
      // 학생 정보 로드
      const students = await getStudents();
      const foundStudent = students.find(s => s.id === studentId);
      if (foundStudent) {
        setStudent(foundStudent);
        setFormData(prev => ({
          ...prev,
          name: foundStudent.name,
          birth: foundStudent.birth,
        }));
      }
      
      // IEP 목록 로드
      const versions = await getIEPVersions(studentId);
      // 최신순 정렬 (년도 내림차순, 학기 내림차순)
      const sortedVersions = [...versions].sort((a, b) => {
        const yearCompare = b.year.localeCompare(a.year);
        if (yearCompare !== 0) return yearCompare;
        return b.semester.localeCompare(a.semester);
      });
      setIepVersions(sortedVersions);
      
      // 최신 IEP 로드
      if (sortedVersions.length > 0) {
        const latest = await getLatestIEP(studentId);
        setCurrentIepId(latest.id);
        loadIEPData(latest.id);
      }
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadIEPData = async (iepId: string) => {
    try {
      // IEP 파일 목록 조회
      const files = await getIEPFiles(iepId);
      const jsonFile = files.find(f => f.file_type === 'student_info');
      
      if (jsonFile) {
        setCurrentIepFileId(jsonFile.id);
        
        // JSON 파일 내용 로드
        try {
          const jsonData = await getIEPFileContent(jsonFile.file_path);
          if (jsonData) {
            // JSON 데이터를 formData에 채우기
            // 도메인 키를 한글로 변환
            const keyToDomain: Record<string, string> = {
              'listeningSpeaking': '듣기⋅말하기',
              'reading': '읽기',
              'writing': '쓰기',
              'grammar': '문법',
              'literature': '문학',
              'mediaLiteracy': '매체',
              'numbersOperations': '수와 연산',
              'changeAndRelations': '변화와 관계',
              'geometryMeasurement': '도형과 측정',
              'dataAndProbability': '자료와 가능성',
            };
            
            // korean_domain과 math_domain이 배열인지 문자열인지 확인
            const koreanDomainArray = Array.isArray(jsonData.korean_domain) 
              ? jsonData.korean_domain 
              : (jsonData.korean_domain ? jsonData.korean_domain.split(', ').filter(Boolean) : []);
            const mathDomainArray = Array.isArray(jsonData.math_domain)
              ? jsonData.math_domain
              : (jsonData.math_domain ? jsonData.math_domain.split(', ').filter(Boolean) : []);
            
            // 영문 키를 한글로 변환
            const koreanDomainsList = koreanDomainArray.map(key => keyToDomain[key] || key).filter(Boolean);
            const mathDomainsList = mathDomainArray.map(key => keyToDomain[key] || key).filter(Boolean);
            
            setFormData(prev => ({
              ...prev,
              name: jsonData.name || prev.name,
              birth: jsonData.birth || prev.birth,
              grade: String(jsonData.grade || ''),
              current_semester: jsonData.current_semester ? `${jsonData.current_semester}학기` : '',
              iep_start_date: jsonData.start_date || '',
              iep_end_date: jsonData.end_date || '',
              guardian_opinion: jsonData.guardian_opinion || '',
              cognitive_level: String(jsonData.cognitive_level || ''),
              social_psych_level: String(jsonData.social_psych_level || ''),
              motor_daily_level: String(jsonData.motor_daily_level || ''),
              vci_score: jsonData.vci_score || 0,
              visual_spatial_score: jsonData.visual_spatial_score || 0,
              fri_score: jsonData.fri_score || 0,
              wmi_score: jsonData.wmi_score || 0,
              psi_score: jsonData.psi_score || 0,
              fsiq_score: jsonData.fsiq_score || 0,
              korean_performance_level: jsonData.korean_performance_level || '',
              math_performance_level: jsonData.math_performance_level || '',
              korean_domain: koreanDomainsList.join(', '),
              math_domain: mathDomainsList.join(', '),
            }));
            
            // 교과목 및 학습 영역 복원
            if (koreanDomainsList.length > 0) {
              setSubject1('국어');
              setKoreanDomains(koreanDomainsList);
            }
            if (mathDomainsList.length > 0) {
              if (koreanDomainsList.length > 0) {
                setSubject2('수학');
              } else {
                setSubject1('수학');
              }
              setMathDomains(mathDomainsList);
            }
          }
        } catch (err) {
          console.error('Error loading JSON content:', err);
          // JSON 로드 실패 시 빈 템플릿 유지
        }
      } else {
        setCurrentIepFileId(null);
        // 파일이 없으면 빈 템플릿으로 초기화
        setFormData(prev => ({
          ...prev,
          grade: '',
          current_semester: '',
          iep_start_date: '',
          iep_end_date: '',
          guardian_opinion: '',
          cognitive_level: '0',
          social_psych_level: '0',
          motor_daily_level: '0',
          vci_score: 0,
          visual_spatial_score: 0,
          fri_score: 0,
          wmi_score: 0,
          psi_score: 0,
          fsiq_score: 0,
          korean_performance_level: '',
          math_performance_level: '',
          korean_domain: '',
          math_domain: '',
        }));
        setSubject1('');
        setSubject2('');
        setKoreanDomains([]);
        setMathDomains([]);
      }
    } catch (err) {
      console.error('Error loading IEP data:', err);
    }
  };

  const handleCreateNewIEP = () => {
    setIsModalOpen(true);
    setModalYear('');
    setModalSemester('');
    setModalError('');
  };

  const handleModalSubmit = async () => {
    if (!studentId) return;
    
    setModalError('');
    
    if (!modalYear || !modalSemester) {
      setModalError('년도와 학기를 모두 입력해주세요.');
      return;
    }
    
    // 중복 체크
    const isDuplicate = iepVersions.some(
      iep => iep.year === modalYear && iep.semester === modalSemester
    );
    
    if (isDuplicate) {
      setModalError('이미 존재하는 학기입니다.');
      return;
    }
    
    try {
      const grade = formData.grade || '1';
      
      const newIEP = await createIEPVersion({
        student_id: studentId,
        year: modalYear,
        semester: modalSemester,
        grade,
      });
      
      // 목록에 추가하고 정렬
      const updatedVersions = [...iepVersions, newIEP].sort((a, b) => {
        const yearCompare = b.year.localeCompare(a.year);
        if (yearCompare !== 0) return yearCompare;
        return b.semester.localeCompare(a.semester);
      });
      setIepVersions(updatedVersions);
      
      setCurrentIepId(newIEP.id);
      setCurrentIepFileId(null);
      setIsEditing(true);
      setIsModalOpen(false);
      
      // 빈 템플릿으로 초기화
      setFormData(prev => ({
        ...prev,
        grade: newIEP.grade,
        current_semester: newIEP.semester,
      }));
      
      // 교과목 초기화
      setSubject1('');
      setSubject2('');
      setKoreanDomains([]);
      setMathDomains([]);
    } catch (err) {
      console.error('Error creating IEP:', err);
      setModalError('IEP 생성에 실패했습니다.');
    }
  };

  const handleIEPClick = async (iepId: string) => {
    setCurrentIepId(iepId);
    await loadIEPData(iepId);
    setIsEditing(false);
    
    // 교과목 초기화
    setSubject1('');
    setSubject2('');
    setKoreanDomains([]);
    setMathDomains([]);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async () => {
    if (!currentIepId) return;
    
    try {
      // JSON 데이터 생성 (백엔드 스키마에 맞게)
      // 도메인을 영문 camelCase로 변환
      const domainToKey: Record<string, string> = {
        '듣기⋅말하기': 'listeningSpeaking',
        '읽기': 'reading',
        '쓰기': 'writing',
        '문법': 'grammar',
        '문학': 'literature',
        '매체': 'mediaLiteracy',
        '수와 연산': 'numbersOperations',
        '변화와 관계': 'changeAndRelations',
        '도형과 측정': 'geometryMeasurement',
        '자료와 가능성': 'dataAndProbability',
      };
      
      const koreanDomainKeys = koreanDomains.map(d => domainToKey[d] || d).filter(Boolean);
      const mathDomainKeys = mathDomains.map(d => domainToKey[d] || d).filter(Boolean);
      
      const jsonData = {
        name: formData.name,
        birth: formData.birth,
        grade: Number(formData.grade) || 1, // int
        current_semester: Number(formData.current_semester.replace('학기', '').trim()) || 1, // int (1 or 2)
        start_date: formData.iep_start_date || '', // 학기 시작일
        end_date: formData.iep_end_date || '', // 학기 종료일
        guardian_opinion: formData.guardian_opinion,
        cognitive_level: formData.cognitive_level, // string
        social_psych_level: formData.social_psych_level, // string
        motor_daily_level: formData.motor_daily_level, // string
        vci_score: formData.vci_score,
        visual_spatial_score: formData.visual_spatial_score,
        fri_score: formData.fri_score,
        wmi_score: formData.wmi_score,
        psi_score: formData.psi_score,
        fsiq_score: formData.fsiq_score,
        korean_performance_level: formData.korean_performance_level,
        math_performance_level: formData.math_performance_level,
        korean_domain: koreanDomainKeys, // List[str]
        math_domain: mathDomainKeys, // List[str]
      };
      
      // JSON을 File 객체로 변환
      const jsonBlob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
      const jsonFile = new File([jsonBlob], `iep_${currentIepId}.json`, { type: 'application/json' });
      
      if (currentIepFileId) {
        // 기존 파일 수정
        await updateIEPFile(currentIepFileId, { file: jsonFile });
      } else {
        // 새 파일 생성
        const fileResponse = await createIEPFile({
          iep_version_id: currentIepId,
          file_type: 'student_info',
          file: jsonFile,
        });
        setCurrentIepFileId(fileResponse.id);
      }
      
      setIsEditing(false);
    } catch (err) {
      console.error('Error saving IEP:', err);
      alert('저장에 실패했습니다.');
    }
  };

  const handleDownload = async () => {
    if (!currentIepId) return;
    
    try {
      const blob = await downloadIEPDocx(currentIepId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `IEP_${currentIepId}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading Word file:', err);
      alert('워드 파일 다운로드에 실패했습니다.');
    }
  };

  const handleSubjectChange = (subject: string, index: number) => {
    // 입력 내용이 있는지 확인
    const hasInput = (index === 0 && subject1 && subject1 !== '교과목 추가하기') ||
                     (index === 1 && subject2 && subject2 !== '교과목 추가하기');
    
    if (hasInput && subject === '교과목 추가하기') {
      const hasDomainSelection = (index === 0 && koreanDomains.length > 0) ||
                                  (index === 1 && mathDomains.length > 0);
      const hasPerformanceLevel = (index === 0 && 
        (subject1 === '국어' ? formData.korean_performance_level : formData.math_performance_level)) ||
        (index === 1 && 
        (subject2 === '국어' ? formData.korean_performance_level : formData.math_performance_level));
      
      if (hasDomainSelection || hasPerformanceLevel) {
        if (!window.confirm('입력한 내용이 모두 지워집니다. 계속하시겠습니까?')) {
          return;
        }
      }
    }
    
    if (index === 0) {
      setSubject1(subject);
      if (subject === '교과목 추가하기') {
        setKoreanDomains([]);
        setMathDomains([]);
        if (subject1 === '국어') {
          setFormData(prev => ({ ...prev, korean_performance_level: '', korean_domain: '' }));
        } else if (subject1 === '수학') {
          setFormData(prev => ({ ...prev, math_performance_level: '', math_domain: '' }));
        }
      }
    } else {
      setSubject2(subject);
      if (subject === '교과목 추가하기') {
        setKoreanDomains([]);
        setMathDomains([]);
        if (subject2 === '국어') {
          setFormData(prev => ({ ...prev, korean_performance_level: '', korean_domain: '' }));
        } else if (subject2 === '수학') {
          setFormData(prev => ({ ...prev, math_performance_level: '', math_domain: '' }));
        }
      }
    }
  };

  const getSubjectOptions = (index: number) => {
    const allOptions = ['교과목 추가하기', '국어', '수학'];
    if (index === 0 && subject2 && subject2 !== '교과목 추가하기') {
      return allOptions.filter(opt => opt === '교과목 추가하기' || opt !== subject2);
    }
    if (index === 1 && subject1 && subject1 !== '교과목 추가하기') {
      return allOptions.filter(opt => opt === '교과목 추가하기' || opt !== subject1);
    }
    return allOptions;
  };

  const getDomainOptions = (subject: string) => {
    if (subject === '국어') {
      return [
        { id: 'listening', label: '듣기⋅말하기' },
        { id: 'reading', label: '읽기' },
        { id: 'writing', label: '쓰기' },
        { id: 'grammar', label: '문법' },
        { id: 'literature', label: '문학' },
        { id: 'media', label: '매체' },
      ];
    } else if (subject === '수학') {
      return [
        { id: 'number', label: '수와 연산' },
        { id: 'change', label: '변화와 관계' },
        { id: 'shape', label: '도형과 측정' },
        { id: 'data', label: '자료와 가능성' },
      ];
    }
    return [];
  };

  const sidebarMenuItems = [
    '+ 새 IEP 만들기',
    ...iepVersions.map(iep => `${iep.year}년 ${iep.semester}학기`),
  ];

  const handleSidebarClick = (item: string) => {
    if (item === '+ 새 IEP 만들기') {
      handleCreateNewIEP();
    } else {
      // IEP 버전 클릭 처리
      const match = item.match(/(\d+)년 (\d+)학기/);
      if (match) {
        const year = match[1];
        const semester = match[2];
        const foundIEP = iepVersions.find(
          iep => iep.year === year && iep.semester === semester
        );
        if (foundIEP) {
          handleIEPClick(foundIEP.id);
        }
      }
    }
  };

  if (isLoading || !student) {
    return (
      <div className="iep-list-page">
        <Header />
        <div className="iep-list-loading">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="iep-list-page">
      <Header />
      
      <div className="iep-list-layout">
        <Sidebar
          title={student.name}
          menuItems={sidebarMenuItems}
          onMenuItemClick={handleSidebarClick}
        />
        
        <main className="iep-list-main">
          <div className="iep-actions">
            <Button
              icon={<img src={penIcon} alt="편집" />}
              onClick={isEditing ? handleSave : handleEdit}
              className={isEditing ? 'button-save' : ''}
            >
              {isEditing ? '저장하기' : '편집하기'}
            </Button>
            <Button
              icon={<img src={downloadIcon} alt="다운로드" />}
              onClick={handleDownload}
            >
              다운로드
            </Button>
          </div>

          <div className="iep-form">
            {/* 영역 1: 기본 정보 */}
            <div className="iep-section">
              <div className="iep-info-grid">
                <div className="iep-field">
                  <label className="iep-field-label">학년</label>
                  <TextBox>
                    <input
                      type="text"
                      value={formData.grade}
                      onChange={(e) => setFormData(prev => ({ ...prev, grade: e.target.value }))}
                      disabled={!isEditing}
                      className="iep-input"
                    />
                  </TextBox>
                </div>
                <div className="iep-field">
                  <label className="iep-field-label">학기</label>
                  <TextBox>
                    <input
                      type="text"
                      value={formData.current_semester}
                      onChange={(e) => setFormData(prev => ({ ...prev, current_semester: e.target.value }))}
                      disabled={!isEditing}
                      className="iep-input"
                    />
                  </TextBox>
                </div>
                <div className="iep-field">
                  <label className="iep-field-label">IEP 시작일</label>
                  <TextBox>
                    <input
                      type="date"
                      value={formData.iep_start_date}
                      onChange={(e) => setFormData(prev => ({ ...prev, iep_start_date: e.target.value }))}
                      disabled={!isEditing}
                      className="iep-input"
                    />
                  </TextBox>
                </div>
                <div className="iep-field">
                  <label className="iep-field-label">IEP 종료일</label>
                  <TextBox>
                    <input
                      type="date"
                      value={formData.iep_end_date}
                      onChange={(e) => setFormData(prev => ({ ...prev, iep_end_date: e.target.value }))}
                      disabled={!isEditing}
                      className="iep-input"
                    />
                  </TextBox>
                </div>
              </div>
              <div className="iep-field-full">
                <label className="iep-field-label">보호자 의견</label>
                <TextBox>
                  <textarea
                    value={formData.guardian_opinion}
                    onChange={(e) => setFormData(prev => ({ ...prev, guardian_opinion: e.target.value }))}
                    disabled={!isEditing}
                    className="iep-input iep-textarea"
                    rows={4}
                  />
                </TextBox>
              </div>
            </div>

            <Line />

            {/* 영역 2: 현재 수행수준 */}
            <div className="iep-section">
              <h2 className="iep-section-title">현재 수행수준</h2>
              <div className="iep-performance-grid">
                <div className="iep-field-full">
                  <label className="iep-field-label">언어/인지면</label>
                  <TextBox>
                    <textarea
                      value={formData.cognitive_level}
                      onChange={(e) => setFormData(prev => ({ ...prev, cognitive_level: e.target.value }))}
                      disabled={!isEditing}
                      className="iep-input iep-textarea"
                      rows={4}
                    />
                  </TextBox>
                </div>
                <div className="iep-field-full">
                  <label className="iep-field-label">사회/심리면</label>
                  <TextBox>
                    <textarea
                      value={formData.social_psych_level}
                      onChange={(e) => setFormData(prev => ({ ...prev, social_psych_level: e.target.value }))}
                      disabled={!isEditing}
                      className="iep-input iep-textarea"
                      rows={4}
                    />
                  </TextBox>
                </div>
                <div className="iep-field-full">
                  <label className="iep-field-label">운동/일상생활면</label>
                  <TextBox>
                    <textarea
                      value={formData.motor_daily_level}
                      onChange={(e) => setFormData(prev => ({ ...prev, motor_daily_level: e.target.value }))}
                      disabled={!isEditing}
                      className="iep-input iep-textarea"
                      rows={4}
                    />
                  </TextBox>
                </div>
              </div>
            </div>

            <Line />

            {/* 영역 3: K-WISC-V */}
            <div className="iep-section">
              <h2 className="iep-section-title">한국 웩슬러 아동지능검사 5판 (K-WISC-V)</h2>
              <div className="iep-wisc-grid">
                {[
                  { key: 'vci_score', label: '언어 이해' },
                  { key: 'visual_spatial_score', label: '시공간' },
                  { key: 'fri_score', label: '유동 추론' },
                  { key: 'wmi_score', label: '작업 기억' },
                  { key: 'psi_score', label: '처리 속도' },
                  { key: 'fsiq_score', label: '전체 지능' },
                ].map(({ key, label }) => (
                  <div key={key} className="iep-field">
                    <label className="iep-field-label">{label}</label>
                    <TextBox>
                      <input
                        type="number"
                        value={formData[key as keyof IEPFormData] as number}
                        onChange={(e) => setFormData(prev => ({ ...prev, [key]: Number(e.target.value) }))}
                        disabled={!isEditing}
                        className="iep-input"
                      />
                    </TextBox>
                  </div>
                ))}
              </div>
            </div>

            <Line />

            {/* 영역 4: 교과목 */}
            <div className="iep-section">
              <h2 className="iep-section-title">교과목</h2>
              
              {/* 교과목 1 */}
              <div className="iep-subject-group">
                <div className="iep-field-full">
                  <Dropdown
                    options={getSubjectOptions(0)}
                    placeholder="교과목 추가하기"
                    onSelect={(option) => handleSubjectChange(option, 0)}
                    disabled={!isEditing}
                  />
                </div>
                
                {subject1 && subject1 !== '교과목 추가하기' && (
                  <>
                    <div className="iep-field-full">
                      <label className="iep-field-label">학습 영역</label>
                      <CheckboxGroup
                        options={getDomainOptions(subject1)}
                        onSelectionChange={(selectedIds) => {
                          const domains = getDomainOptions(subject1)
                            .filter(opt => selectedIds.includes(opt.id))
                            .map(opt => opt.label);
                          if (subject1 === '국어') {
                            setKoreanDomains(domains);
                            setFormData(prev => ({ ...prev, korean_domain: domains.join(', ') }));
                          } else {
                            setMathDomains(domains);
                            setFormData(prev => ({ ...prev, math_domain: domains.join(', ') }));
                          }
                        }}
                      />
                    </div>
                    <div className="iep-field-full">
                      <label className="iep-field-label">지난학기 수행수준</label>
                      <TextBox>
                        <textarea
                          value={subject1 === '국어' ? formData.korean_performance_level : formData.math_performance_level}
                          onChange={(e) => {
                            if (subject1 === '국어') {
                              setFormData(prev => ({ ...prev, korean_performance_level: e.target.value }));
                            } else {
                              setFormData(prev => ({ ...prev, math_performance_level: e.target.value }));
                            }
                          }}
                          disabled={!isEditing}
                          className="iep-input iep-textarea"
                          rows={3}
                        />
                      </TextBox>
                    </div>
                    <div className="iep-field-full iep-button-right">
                      <Button
                        arrowDirection="right"
                        onClick={() => navigate(`/students/${studentId}/iep-versions/${currentIepId}/syllabus?subject=${subject1}`)}
                      >
                        교육계획
                      </Button>
                    </div>
                  </>
                )}
              </div>

              {/* 교과목 2 */}
              <div className="iep-subject-group">
                <div className="iep-field-full">
                  <Dropdown
                    options={getSubjectOptions(1)}
                    placeholder="교과목 추가하기"
                    onSelect={(option) => handleSubjectChange(option, 1)}
                    disabled={!isEditing}
                  />
                </div>
                
                {subject2 && subject2 !== '교과목 추가하기' && (
                  <>
                    <div className="iep-field-full">
                      <label className="iep-field-label">학습 영역</label>
                      <CheckboxGroup
                        options={getDomainOptions(subject2)}
                        onSelectionChange={(selectedIds) => {
                          const domains = getDomainOptions(subject2)
                            .filter(opt => selectedIds.includes(opt.id))
                            .map(opt => opt.label);
                          if (subject2 === '국어') {
                            setKoreanDomains(domains);
                            setFormData(prev => ({ ...prev, korean_domain: domains.join(', ') }));
                          } else {
                            setMathDomains(domains);
                            setFormData(prev => ({ ...prev, math_domain: domains.join(', ') }));
                          }
                        }}
                      />
                    </div>
                    <div className="iep-field-full">
                      <label className="iep-field-label">지난학기 수행수준</label>
                      <TextBox>
                        <textarea
                          value={subject2 === '국어' ? formData.korean_performance_level : formData.math_performance_level}
                          onChange={(e) => {
                            if (subject2 === '국어') {
                              setFormData(prev => ({ ...prev, korean_performance_level: e.target.value }));
                            } else {
                              setFormData(prev => ({ ...prev, math_performance_level: e.target.value }));
                            }
                          }}
                          disabled={!isEditing}
                          className="iep-input iep-textarea"
                          rows={3}
                        />
                      </TextBox>
                    </div>
                    <div className="iep-field-full iep-button-right">
                      <Button
                        arrowDirection="right"
                        onClick={() => navigate(`/students/${studentId}/iep-versions/${currentIepId}/syllabus?subject=${subject2}`)}
                      >
                        교육계획
                      </Button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* 새 IEP 생성 모달 */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">새 IEP 만들기</h2>
              <button className="modal-close" onClick={() => setIsModalOpen(false)}>
                ×
              </button>
            </div>
            
            <div className="modal-form">
              <div className="form-group">
                <label htmlFor="modal-year" className="form-label">
                  년도
                </label>
                <input
                  id="modal-year"
                  type="text"
                  value={modalYear}
                  onChange={(e) => setModalYear(e.target.value.replace(/\D/g, ''))}
                  className="form-input"
                  placeholder="예: 2025"
                  maxLength={4}
                />
              </div>

              <div className="form-group">
                <label htmlFor="modal-semester" className="form-label">
                  학기
                </label>
                <input
                  id="modal-semester"
                  type="text"
                  value={modalSemester}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '');
                    if (value === '' || value === '1' || value === '2') {
                      setModalSemester(value);
                    }
                  }}
                  className="form-input"
                  placeholder="1 또는 2"
                  maxLength={1}
                />
              </div>

              {modalError && <div className="form-error">{modalError}</div>}

              <div className="modal-actions">
                <button
                  type="button"
                  className="modal-button cancel"
                  onClick={() => setIsModalOpen(false)}
                >
                  취소
                </button>
                <button
                  type="button"
                  className="modal-button submit"
                  onClick={handleModalSubmit}
                >
                  생성
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IEPList;
