import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { Header, Line, Button, TabButton } from '../components';
import { 
  getIEPFiles,
  getIEPFileContent,
  createIEPFile,
  updateIEPFile,
  type IEPFile
} from '../utils/api';
import penIcon from '../assets/images/pen.png';
import starIcon from '../assets/images/star.png';
import './Syllabus.css';

// 도메인 라벨 -> JSON 키 매핑
const DOMAIN_TO_KEY: Record<string, string> = {
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

interface GoalData {
  [key: string]: string; // annual_xxx_goal, semester_xxx_goal
}

interface WeeklyContent {
  [key: string]: string[]; // domain_weeklyContent: string[]
}

interface WeeklyMaterial {
  [key: string]: string[]; // domain_weekly_material: string[]
}

const SyllabusPage: React.FC = () => {
  const { studentId, iepVersionId } = useParams<{ studentId: string; iepVersionId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const subject = searchParams.get('subject') || '국어';

  // 학생 정보 및 도메인
  const [domains, setDomains] = useState<string[]>([]);
  const [goalFile, setGoalFile] = useState<IEPFile | null>(null);
  const [weeklyContentFile, setWeeklyContentFile] = useState<IEPFile | null>(null);
  const [weeklyMaterialFile, setWeeklyMaterialFile] = useState<IEPFile | null>(null);

  // 학습 목표 영역
  const [isEditingGoals, setIsEditingGoals] = useState(false);
  const [goalData, setGoalData] = useState<GoalData>({});

  // 교육 계획 영역
  const [isEditingPlan, setIsEditingPlan] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [weeklyContent, setWeeklyContent] = useState<WeeklyContent>({});
  const [weeklyMaterial, setWeeklyMaterial] = useState<WeeklyMaterial>({});

  // ---------------------------
  // 데이터 로드
  // ---------------------------
  useEffect(() => {
    if (iepVersionId) {
      loadData();
    }
  }, [iepVersionId, subject]);

  const loadData = async () => {
    if (!iepVersionId) return;

    try {
      // IEP 파일 목록 조회
      const files = await getIEPFiles(iepVersionId);
      
      // 학생 정보 파일에서 도메인 추출
      const studentInfoFile = files.find(f => f.file_type === 'student_info');
      let domainList: string[] = [];
      
      if (studentInfoFile) {
        try {
          const studentData = await getIEPFileContent(studentInfoFile.file_path);
          const domainKey = subject === '국어' ? 'korean_domain' : 'math_domain';
          const domainString = studentData?.[domainKey] || '';
          domainList = domainString.split(', ').filter(Boolean);
        } catch (err) {
          console.error('Error loading student info:', err);
        }
      }
      
      if (domainList.length === 0) {
        // 도메인이 없으면 빈 상태로 표시
        setDomains([]);
        setSelectedDomain('');
        setGoalData({});
        setWeeklyContent({});
        setWeeklyMaterial({});
        setGoalFile(null);
        setWeeklyContentFile(null);
        setWeeklyMaterialFile(null);
        return;
      }
      
      setDomains(domainList);
      if (domainList.length > 0) {
        setSelectedDomain(domainList[0]);
      }

      // 목표 파일 로드
      const foundGoalFile = files.find(f => f.file_type === 'goal');
      if (foundGoalFile) {
        setGoalFile(foundGoalFile);
        try {
          const goalContent = await getIEPFileContent(foundGoalFile.file_path);
          const goals: GoalData = {};
          domainList.forEach((domain: string) => {
            const domainKey = DOMAIN_TO_KEY[domain];
            if (domainKey) {
              goals[`annual_${domainKey}_goal`] = goalContent?.[`annual_${domainKey}_goal`] || '';
              goals[`semester_${domainKey}_goal`] = goalContent?.[`semester_${domainKey}_goal`] || '';
            }
          });
          setGoalData(goals);
        } catch (err) {
          console.error('Error loading goal file:', err);
        }
      }

      // 주차별 학습 내용 파일 로드
      const foundWeeklyContentFile = files.find(f => f.file_type === 'weekly_content');
      if (foundWeeklyContentFile) {
        setWeeklyContentFile(foundWeeklyContentFile);
        try {
          const weeklyContentData = await getIEPFileContent(foundWeeklyContentFile.file_path);
          const weekly: WeeklyContent = {};
          domainList.forEach((domain: string) => {
            const domainKey = DOMAIN_TO_KEY[domain];
            if (domainKey) {
              const existingContent = weeklyContentData?.[`${domainKey}_weeklyContent`];
              weekly[`${domainKey}_weeklyContent`] = existingContent && Array.isArray(existingContent) 
                ? existingContent 
                : Array(20).fill('');
            }
          });
          setWeeklyContent(weekly);
        } catch (err) {
          console.error('Error loading weekly content file:', err);
        }
      }

      // 주차별 교육자료 파일 로드
      const foundWeeklyMaterialFile = files.find(f => f.file_type === 'weekly_material');
      if (foundWeeklyMaterialFile) {
        setWeeklyMaterialFile(foundWeeklyMaterialFile);
        try {
          const weeklyMaterialData = await getIEPFileContent(foundWeeklyMaterialFile.file_path);
          const material: WeeklyMaterial = {};
          domainList.forEach((domain: string) => {
            const domainKey = DOMAIN_TO_KEY[domain];
            if (domainKey) {
              const existingMaterial = weeklyMaterialData?.[`${domainKey}_weekly_material`];
              material[`${domainKey}_weekly_material`] = existingMaterial && Array.isArray(existingMaterial)
                ? existingMaterial
                : Array(20).fill('');
            }
          });
          setWeeklyMaterial(material);
        } catch (err) {
          console.error('Error loading weekly material file:', err);
        }
      }
    } catch (err) {
      console.error('Error loading data:', err);
      // 에러 발생 시 빈 상태로 표시
      setDomains([]);
      setSelectedDomain('');
      setGoalData({});
      setWeeklyContent({});
      setWeeklyMaterial({});
    }
  };

  // ---------------------------
  // 학습 목표 AI 추천
  // ---------------------------
  const handleAIGoalRecommend = async () => {
    if (!iepVersionId) {
      alert('IEP 버전 정보가 없습니다.');
      return;
    }

    try {
      // TODO: 백엔드 API 호출
      // const response = await fetch('/api/ai/recommend-goals', {
      //   method: 'POST',
      //   body: JSON.stringify(studentInfo),
      // });
      // const recommendedGoals = await response.json();

      // TODO: 백엔드 API 호출로 실제 추천 받기
      // 임시로 빈 목표 설정 (실제로는 API 응답 사용)
      const recommendedGoals: GoalData = {};
      domains.forEach(domain => {
        const domainKey = DOMAIN_TO_KEY[domain];
        if (domainKey) {
          recommendedGoals[`annual_${domainKey}_goal`] = `[AI 추천] ${domain} 영역의 연간 학습 목표입니다.`;
          recommendedGoals[`semester_${domainKey}_goal`] = `[AI 추천] ${domain} 영역의 학기 학습 목표입니다.`;
        }
      });

      setGoalData(recommendedGoals);
      
      // 자동 저장
      await saveGoalData(recommendedGoals);
    } catch (err) {
      console.error('Error getting AI recommendations:', err);
      alert('AI 추천을 가져오는데 실패했습니다.');
    }
  };

  // ---------------------------
  // 학습 목표 저장
  // ---------------------------
  const saveGoalData = async (data?: GoalData) => {
    if (!iepVersionId) {
      alert('IEP 버전 정보가 없습니다.');
      return;
    }

    const dataToSave = data || goalData;

    try {
      const jsonBlob = new Blob([JSON.stringify(dataToSave, null, 2)], { type: 'application/json' });
      const jsonFile = new File([jsonBlob], `goal_${iepVersionId}.json`, { type: 'application/json' });
      
      if (goalFile) {
        // 기존 파일 업데이트
        await updateIEPFile(goalFile.id, { file: jsonFile });
      } else {
        // 새 파일 생성
        const newFile = await createIEPFile({
          iep_version_id: iepVersionId,
          file_type: 'goal',
          file: jsonFile,
        });
        setGoalFile(newFile);
      }
      
      setIsEditingGoals(false);
    } catch (err) {
      console.error('Error saving goal data:', err);
      alert('저장에 실패했습니다.');
    }
  };

  // ---------------------------
  // 교육 계획 AI 추천 (교육 내용)
  // ---------------------------
  const handleAIContentRecommend = async () => {
    if (!iepVersionId || !selectedDomain) return;

    try {
      // TODO: 백엔드 API 호출
      // const response = await fetch('/api/ai/recommend-weekly-content', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     studentInfo,
      //     goals: goalData,
      //     domain: DOMAIN_TO_KEY[selectedDomain],
      //   }),
      // });
      // const recommended = await response.json();

      const domainKey = DOMAIN_TO_KEY[selectedDomain];
      if (!domainKey) return;

      const weeklyKey = `${domainKey}_weeklyContent`;
      
      // TODO: 백엔드 API 호출
      // const response = await fetch('/api/ai/recommend-weekly-content', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     studentInfo,
      //     goals: goalData,
      //     domain: domainKey,
      //   }),
      // });
      // const recommendedContent = await response.json()[weeklyKey];
      
      // TODO: 실제 API 응답 사용
      // 임시 더미 데이터
      const recommendedContent = Array(20).fill(`${selectedDomain} 영역의 교육 내용을 추천합니다.`);
      
      const updatedContent = { ...weeklyContent, [weeklyKey]: recommendedContent };
      setWeeklyContent(updatedContent);
      
      // 자동 저장
      const jsonBlob = new Blob([JSON.stringify(updatedContent, null, 2)], { type: 'application/json' });
      const jsonFile = new File([jsonBlob], `weekly_content_${iepVersionId}.json`, { type: 'application/json' });
      
      if (weeklyContentFile) {
        await updateIEPFile(weeklyContentFile.id, { file: jsonFile });
      } else {
        const newFile = await createIEPFile({
          iep_version_id: iepVersionId,
          file_type: 'weekly_content',
          file: jsonFile,
        });
        setWeeklyContentFile(newFile);
      }
    } catch (err) {
      console.error('Error getting AI recommendations:', err);
      alert('AI 추천을 가져오는데 실패했습니다.');
    }
  };

  // ---------------------------
  // 교육 계획 AI 추천 (교육자료)
  // ---------------------------
  const handleAIMaterialRecommend = async () => {
    if (!iepVersionId || !selectedDomain) return;

    try {
      // TODO: 백엔드 API 호출
      // const response = await fetch('/api/ai/recommend-weekly-material', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     studentInfo,
      //     goals: goalData,
      //     domain: DOMAIN_TO_KEY[selectedDomain],
      //     content: weeklyContent[`${DOMAIN_TO_KEY[selectedDomain]}_weeklyContent`],
      //   }),
      // });
      // const recommended = await response.json();

      const domainKey = DOMAIN_TO_KEY[selectedDomain];
      if (!domainKey) return;

      const materialKey = `${domainKey}_weekly_material`;
      const contentKey = `${domainKey}_weeklyContent`;
      const currentContent = weeklyContent[contentKey] || [];
      
      // TODO: 백엔드 API 호출
      // const response = await fetch('/api/ai/recommend-weekly-material', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     studentInfo,
      //     goals: goalData,
      //     domain: domainKey,
      //     content: currentContent,
      //   }),
      // });
      // const recommendedMaterial = await response.json()[materialKey];
      
      // TODO: 실제 API 응답 사용
      // 교육 내용이 있는 주차만 교육자료 추천
      const recommendedMaterial = currentContent.map((content) => 
        content ? `${selectedDomain} 영역의 교육자료를 추천합니다.` : ''
      );
      
      const updatedMaterial = { ...weeklyMaterial, [materialKey]: recommendedMaterial };
      setWeeklyMaterial(updatedMaterial);
      
      // 자동 저장
      const jsonBlob = new Blob([JSON.stringify(updatedMaterial, null, 2)], { type: 'application/json' });
      const jsonFile = new File([jsonBlob], `weekly_material_${iepVersionId}.json`, { type: 'application/json' });
      
      if (weeklyMaterialFile) {
        await updateIEPFile(weeklyMaterialFile.id, { file: jsonFile });
      } else {
        const newFile = await createIEPFile({
          iep_version_id: iepVersionId,
          file_type: 'weekly_material',
          file: jsonFile,
        });
        setWeeklyMaterialFile(newFile);
      }
    } catch (err) {
      console.error('Error getting AI recommendations:', err);
      alert('AI 추천을 가져오는데 실패했습니다.');
    }
  };

  // ---------------------------
  // 교육 계획 저장
  // ---------------------------
  const savePlanData = async () => {
    if (!iepVersionId) {
      alert('IEP 버전 정보가 없습니다.');
      return;
    }

    try {
      // 주차별 학습 내용 저장
      const contentJsonBlob = new Blob([JSON.stringify(weeklyContent, null, 2)], { type: 'application/json' });
      const contentJsonFile = new File([contentJsonBlob], `weekly_content_${iepVersionId}.json`, { type: 'application/json' });
      
      if (weeklyContentFile) {
        await updateIEPFile(weeklyContentFile.id, { file: contentJsonFile });
      } else {
        const newContentFile = await createIEPFile({
          iep_version_id: iepVersionId,
          file_type: 'weekly_content',
          file: contentJsonFile,
        });
        setWeeklyContentFile(newContentFile);
      }

      // 주차별 교육자료 저장
      const materialJsonBlob = new Blob([JSON.stringify(weeklyMaterial, null, 2)], { type: 'application/json' });
      const materialJsonFile = new File([materialJsonBlob], `weekly_material_${iepVersionId}.json`, { type: 'application/json' });
      
      if (weeklyMaterialFile) {
        await updateIEPFile(weeklyMaterialFile.id, { file: materialJsonFile });
      } else {
        const newMaterialFile = await createIEPFile({
          iep_version_id: iepVersionId,
          file_type: 'weekly_material',
          file: materialJsonFile,
        });
        setWeeklyMaterialFile(newMaterialFile);
      }
      
      setIsEditingPlan(false);
    } catch (err) {
      console.error('Error saving plan data:', err);
      alert('저장에 실패했습니다.');
    }
  };

  // ---------------------------
  // 렌더링
  // ---------------------------
  const getDomainKey = (domain: string) => DOMAIN_TO_KEY[domain] || '';

  return (
    <div className="syllabus-page">
      <Header />

      {/* 과목 이름 바 */}
      <div className="subject-bar">
        <div className="subject-bar-content">
          <h1 className="subject-name">{subject}</h1>
        </div>
      </div>

      <div className="syllabus-container">

        {/* 학습 목표 영역 */}
        <div className="syllabus-section">
          <div className="section-header">
            <h2 className="section-title">학습 목표</h2>
            <div className="section-actions">
              <Button
                icon={<img src={penIcon} alt="편집" />}
                onClick={isEditingGoals ? () => saveGoalData() : () => setIsEditingGoals(true)}
                className={isEditingGoals ? 'button-save' : ''}
              >
                {isEditingGoals ? '저장하기' : '편집하기'}
              </Button>
              <Button
                icon={<img src={starIcon} alt="AI" />}
                onClick={handleAIGoalRecommend}
                className="ai-button"
              >
                AI
              </Button>
            </div>
          </div>

          {/* 연간 목표 표 */}
          <div className="goal-table-container">
            <h3 className="goal-table-title">연간 목표</h3>
            {domains.length > 0 ? (
              <table className="goal-table">
                <tbody>
                  {domains.map((domain) => {
                    const domainKey = getDomainKey(domain);
                    const goalKey = `annual_${domainKey}_goal`;
                    return (
                      <tr key={domain}>
                        <td className="goal-domain-cell">{domain}</td>
                        <td className="goal-content-cell">
                          {isEditingGoals ? (
                            <textarea
                              className="goal-input"
                              value={goalData[goalKey] || ''}
                              onChange={(e) => setGoalData({ ...goalData, [goalKey]: e.target.value })}
                            />
                          ) : (
                            <div className="goal-text">{goalData[goalKey] || ''}</div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <div className="empty-message">도메인이 선택되지 않았습니다.</div>
            )}
          </div>

          {/* 학기 목표 표 */}
          <div className="goal-table-container">
            <h3 className="goal-table-title">학기 목표</h3>
            {domains.length > 0 ? (
              <table className="goal-table">
                <tbody>
                  {domains.map((domain) => {
                    const domainKey = getDomainKey(domain);
                    const goalKey = `semester_${domainKey}_goal`;
                    return (
                      <tr key={domain}>
                        <td className="goal-domain-cell">{domain}</td>
                        <td className="goal-content-cell">
                          {isEditingGoals ? (
                            <textarea
                              className="goal-input"
                              value={goalData[goalKey] || ''}
                              onChange={(e) => setGoalData({ ...goalData, [goalKey]: e.target.value })}
                            />
                          ) : (
                            <div className="goal-text">{goalData[goalKey] || ''}</div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <div className="empty-message">도메인이 선택되지 않았습니다.</div>
            )}
          </div>
        </div>

        <Line />

        {/* 교육 계획 영역 */}
        <div className="syllabus-section">
          <div className="section-header">
            <h2 className="section-title">교육 계획</h2>
          </div>

          {/* 도메인 탭 */}
          <div className="domain-tabs">
            {domains.map((domain) => (
              <TabButton
                key={domain}
                isSelected={selectedDomain === domain}
                onClick={() => setSelectedDomain(domain)}
              >
                {domain}
              </TabButton>
            ))}
            <div className="domain-tabs-actions">
              <Button
                icon={<img src={penIcon} alt="편집" />}
                onClick={isEditingPlan ? savePlanData : () => setIsEditingPlan(true)}
                className={isEditingPlan ? 'button-save' : ''}
              >
                {isEditingPlan ? '저장하기' : '편집하기'}
              </Button>
            </div>
          </div>

          {/* 주차별 교육 계획 표 */}
          {selectedDomain && (
            <div className="plan-table-container">
              <table className="plan-table">
                <tbody>
                  {/* 헤더 행 */}
                  <tr className="plan-header-row">
                    <td className="plan-header-cell plan-empty-cell"></td>
                    <td className="plan-header-cell plan-content-header">
                      <span>교육 내용</span>
                      {isEditingPlan && (
                        <Button
                          icon={<img src={starIcon} alt="AI" />}
                          onClick={handleAIContentRecommend}
                          className="ai-button-small"
                        >
                          AI
                        </Button>
                      )}
                    </td>
                    <td className="plan-header-cell plan-material-header">
                      <span>교육자료</span>
                      {isEditingPlan && (
                        <Button
                          icon={<img src={starIcon} alt="AI" />}
                          onClick={handleAIMaterialRecommend}
                          className="ai-button-small"
                        >
                          AI
                        </Button>
                      )}
                    </td>
                  </tr>
                  {/* 데이터 행 */}
                  {Array.from({ length: 20 }, (_, i) => i + 1).map((week) => {
                    const domainKey = getDomainKey(selectedDomain);
                    const weeklyKey = `${domainKey}_weeklyContent`;
                    const materialKey = `${domainKey}_weekly_material`;
                    const content = weeklyContent[weeklyKey]?.[week - 1] || '';
                    const material = weeklyMaterial[materialKey]?.[week - 1] || '';
                    
                    return (
                      <tr key={week}>
                        <td className="plan-week-number">{week}</td>
                        <td className="plan-content-cell">
                          {isEditingPlan ? (
                            <textarea
                              className="plan-content-input"
                              value={content}
                              onChange={(e) => {
                                const updated = [...(weeklyContent[weeklyKey] || Array(20).fill(''))];
                                updated[week - 1] = e.target.value;
                                setWeeklyContent({ ...weeklyContent, [weeklyKey]: updated });
                              }}
                            />
                          ) : (
                            <div className="plan-content-text">{content}</div>
                          )}
                        </td>
                        <td className="plan-material-cell">
                          {isEditingPlan ? (
                            <textarea
                              className="plan-content-input"
                              value={material}
                              placeholder="교육자료를 입력하세요"
                              onChange={(e) => {
                                const updated = [...(weeklyMaterial[materialKey] || Array(20).fill(''))];
                                updated[week - 1] = e.target.value;
                                setWeeklyMaterial({ ...weeklyMaterial, [materialKey]: updated });
                              }}
                            />
                          ) : (
                            <div className="plan-content-text">{material || '-'}</div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* 학생특성 버튼 */}
        <div className="syllabus-footer">
          <Button
            arrowDirection="left"
            onClick={() => navigate(`/students/${studentId}/iep-versions`)}
          >
            학생특성
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SyllabusPage;

