import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { Header, Line, Button, TabButton } from '../components';
import { 
  getIEPFiles,
  createIEPFile,
  updateIEPFile,
  type IEPFile
} from '../utils/api';

const API_BASE_URL = 'http://localhost:8000';
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
        const studentData = studentInfoFile.file_content;
        const domainKey = subject === '국어' ? 'korean_domain' : 'math_domain';
        const domainData = studentData?.[domainKey];
        
        // 배열인지 문자열인지 확인하고 처리
        if (Array.isArray(domainData)) {
          // 배열인 경우: 영문 키를 한글로 변환
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
          domainList = domainData.map((key: string) => keyToDomain[key] || key).filter(Boolean);
        } else if (typeof domainData === 'string' && domainData) {
          // 문자열인 경우: 기존 로직 유지
          domainList = domainData.split(', ').filter(Boolean);
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
        const goalContent = foundGoalFile.file_content;
        const goals: GoalData = {};
        domainList.forEach((domain: string) => {
          const domainKey = DOMAIN_TO_KEY[domain];
          if (domainKey) {
            goals[`annual_${domainKey}_goal`] = goalContent?.[`annual_${domainKey}_goal`] || '';
            goals[`semester_${domainKey}_goal`] = goalContent?.[`semester_${domainKey}_goal`] || '';
          }
        });
        setGoalData(goals);
      }

      // 주차별 학습 내용 파일 로드
      const foundWeeklyContentFile = files.find(f => f.file_type === 'weekly_content');
      if (foundWeeklyContentFile) {
        setWeeklyContentFile(foundWeeklyContentFile);
        const weeklyContentData = foundWeeklyContentFile.file_content;
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
      }

      // 주차별 교육자료 파일 로드
      const foundWeeklyMaterialFile = files.find(f => f.file_type === 'weekly_material');
      if (foundWeeklyMaterialFile) {
        setWeeklyMaterialFile(foundWeeklyMaterialFile);
        const weeklyMaterialData = foundWeeklyMaterialFile.file_content;
        const material: WeeklyMaterial = {};
        domainList.forEach((domain: string) => {
          const domainKey = DOMAIN_TO_KEY[domain];
          if (domainKey) {
            const materialKey = `${domainKey}_weekly_material`;
            const existingMaterial = weeklyMaterialData?.[materialKey];
            
            let materialArray: string[] = [];
            
            if (existingMaterial && Array.isArray(existingMaterial)) {
              // 백엔드가 스펙 형식으로 저장한 경우: [{week: number, materials: [{title, url, ...}]}, ...]
              if (existingMaterial.length > 0 && existingMaterial[0] && typeof existingMaterial[0] === 'object' && 'materials' in existingMaterial[0]) {
                // 스펙 형식: 주차별로 정렬하고 materials[0].title과 url 추출
                materialArray = existingMaterial
                  .sort((a: any, b: any) => (a.week || 0) - (b.week || 0))
                  .map((item: any) => {
                    if (item.materials && Array.isArray(item.materials) && item.materials.length > 0) {
                      const material = item.materials[0];
                      const title = material.title || '';
                      const url = material.url || '';
                      
                      // title이 있으면 "제목 - URL" 형식으로, 없으면 URL만 표시
                      if (title && url) {
                        return `${title} - ${url}`;
                      } else if (title) {
                        return title;
                      } else if (url) {
                        return url;
                      }
                    }
                    return '';
                  });
              } else {
                // 이미 문자열 배열 형식인 경우
                materialArray = existingMaterial.map((item: any) => {
                  if (typeof item === 'string') {
                    return item;
                  }
                  // 객체인 경우 URL 추출 시도
                  return item.url || item.content_url || item.material_url || '';
                });
              }
            }
            
            // 20주차가 아니면 빈 문자열로 채움
            while (materialArray.length < 20) {
              materialArray.push('');
            }
            materialArray = materialArray.slice(0, 20);
            
            material[materialKey] = materialArray;
          }
        });
        setWeeklyMaterial(material);
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
      // 학생 정보 파일 가져오기
      const files = await getIEPFiles(iepVersionId);
      const studentInfoFile = files.find(f => f.file_type === 'student_info');
      
      if (!studentInfoFile) {
        alert('학생 정보 파일이 없습니다. 먼저 학생 정보를 저장해주세요.');
        return;
      }

      // 학생 프로필 데이터 로드
      const studentProfile = studentInfoFile.file_content;
      
      // 백엔드 API 호출: AI 목표 추천
      const formData = new FormData();
      const studentProfileBlob = new Blob([JSON.stringify(studentProfile, null, 2)], { type: 'application/json' });
      const studentProfileFile = new File([studentProfileBlob], 'student_info.json', { type: 'application/json' });
      
      formData.append('iep_version_id', iepVersionId);
      formData.append('file_type', 'goal'); // 백엔드는 "goal" 사용
      formData.append('file', studentProfileFile);

      const response = await fetch(`${API_BASE_URL}/iep-files`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('AI 목표 추천에 실패했습니다.');
      }

      const createdFile = await response.json();
      
      // 생성된 파일 내용 로드
      const goalContent = createdFile.file_content;
      
      // 백엔드가 이미 변환해서 반환: {annual_{domain}_goal, semester_{domain}_goal} 형식
      // 프론트엔드 형식에 맞게 그대로 사용
      const recommendedGoals: GoalData = {};
      domains.forEach(domain => {
        const domainKey = DOMAIN_TO_KEY[domain];
        if (domainKey) {
          // 백엔드가 이미 annual_{domainKey}_goal 형식으로 반환함
          recommendedGoals[`annual_${domainKey}_goal`] = goalContent[`annual_${domainKey}_goal`] || '';
          recommendedGoals[`semester_${domainKey}_goal`] = goalContent[`semester_${domainKey}_goal`] || '';
        }
      });

      setGoalData(recommendedGoals);
      setGoalFile(createdFile);
      
      // 백엔드에서 이미 저장되었으므로 추가 저장 불필요
      alert('AI 목표 추천이 완료되었습니다.');
    } catch (err) {
      console.error('Error getting AI recommendations:', err);
      const errorMessage = err instanceof Error ? err.message : 'AI 추천을 가져오는데 실패했습니다.';
      console.error('Full error:', err);
      alert(`AI 추천 실패: ${errorMessage}`);
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
      // 학생 정보 파일 가져오기
      const files = await getIEPFiles(iepVersionId);
      const studentInfoFile = files.find(f => f.file_type === 'student_info');
      
      if (!studentInfoFile) {
        alert('학생 정보 파일이 없습니다. 먼저 학생 정보를 저장해주세요.');
        return;
      }

      // 학생 프로필 데이터 로드
      const studentProfile = studentInfoFile.file_content;
      
      // 백엔드 API 호출: AI 주차별 학습 내용 추천
      const formData = new FormData();
      const studentProfileBlob = new Blob([JSON.stringify(studentProfile, null, 2)], { type: 'application/json' });
      const studentProfileFile = new File([studentProfileBlob], 'student_info.json', { type: 'application/json' });
      
      formData.append('iep_version_id', iepVersionId);
      formData.append('file_type', 'weekly_content'); // 백엔드는 "weekly_content" 사용
      formData.append('file', studentProfileFile);

      const response = await fetch(`${API_BASE_URL}/iep-files`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('AI 학습 내용 추천에 실패했습니다.');
      }

      const createdFile = await response.json();
      
      // 생성된 파일 내용 로드
      const weeklyPlanContent = createdFile.file_content;
      
      // 백엔드 응답 형식 변환: {domain_key: [{week, content}, ...]} → {domain_key_weeklyContent: [content, ...]}
      const domainKey = DOMAIN_TO_KEY[selectedDomain];
      if (!domainKey) return;

      const weeklyKey = `${domainKey}_weeklyContent`;
      
      // 백엔드 응답이 {domain_key: [{week: 1, content: "..."}, ...]} 형식인 경우
      let recommendedContent: string[] = [];
      if (weeklyPlanContent[domainKey] && Array.isArray(weeklyPlanContent[domainKey])) {
        // 주차별로 정렬하고 content만 추출
        recommendedContent = weeklyPlanContent[domainKey]
          .sort((a: any, b: any) => a.week - b.week)
          .map((item: any) => item.content || '');
      } else if (weeklyPlanContent[weeklyKey] && Array.isArray(weeklyPlanContent[weeklyKey])) {
        // 이미 {domain_key_weeklyContent: [...]} 형식인 경우
        recommendedContent = weeklyPlanContent[weeklyKey];
      }
      
      // 20주차가 아니면 빈 문자열로 채움
      while (recommendedContent.length < 20) {
        recommendedContent.push('');
      }
      recommendedContent = recommendedContent.slice(0, 20);
      
      const updatedContent = { ...weeklyContent, [weeklyKey]: recommendedContent };
      setWeeklyContent(updatedContent);
      setWeeklyContentFile(createdFile);
      
      // 자동 저장 (이미 백엔드에 저장되었지만, 프론트엔드 형식으로도 저장)
      const jsonBlob = new Blob([JSON.stringify(updatedContent, null, 2)], { type: 'application/json' });
      const jsonFile = new File([jsonBlob], `weekly_content_${iepVersionId}.json`, { type: 'application/json' });
      
      await updateIEPFile(createdFile.id, { file: jsonFile });
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
      // 주차별 학습 내용 파일이 필요함 (교육자료 추천을 위해)
      if (!weeklyContentFile) {
        alert('먼저 주차별 학습 내용을 생성해주세요.');
        return;
      }

      // 주차별 학습 내용 로드
      // weeklyContentFile.file_content 또는 weeklyContent state에서 가져오기
      const weeklyContentData = weeklyContentFile.file_content || {};
      
      // 선택된 도메인의 학습 내용이 있는지 확인
      const domainKey = DOMAIN_TO_KEY[selectedDomain];
      if (!domainKey) {
        alert('도메인 정보를 찾을 수 없습니다.');
        return;
      }
      
      const weeklyContentKey = `${domainKey}_weeklyContent`;
      
      // 두 곳에서 확인: file_content와 state
      const weeklyContentListFromFile = weeklyContentData?.[weeklyContentKey];
      const weeklyContentListFromState = weeklyContent[weeklyContentKey];
      const weeklyContentList = weeklyContentListFromFile || weeklyContentListFromState;
      
      // 디버깅: 데이터 확인
      console.log('교육자료 추천 검증:', {
        selectedDomain,
        domainKey,
        weeklyContentKey,
        weeklyContentData,
        weeklyContentListFromFile,
        weeklyContentListFromState,
        weeklyContentList,
        isArray: Array.isArray(weeklyContentList),
        length: weeklyContentList?.length,
        firstItem: weeklyContentList?.[0],
        hasContent: weeklyContentList && Array.isArray(weeklyContentList) && weeklyContentList.length > 0 && weeklyContentList.some((item: string) => item && typeof item === 'string' && item.trim().length > 0)
      });
      
      // 학습 내용이 없거나 빈 배열인지 확인
      // 배열이 있고, 길이가 0보다 크고, 실제 내용이 있는 항목이 하나라도 있어야 함
      const hasValidContent = weeklyContentList && 
                              Array.isArray(weeklyContentList) && 
                              weeklyContentList.length > 0 && 
                              weeklyContentList.some((item: string) => item && typeof item === 'string' && item.trim().length > 0);
      
      if (!hasValidContent) {
        alert(`${selectedDomain} 도메인의 주차별 학습 내용이 없습니다. 먼저 해당 도메인의 학습 내용을 생성해주세요.`);
        return;
      }
      
      // 백엔드 API 호출: AI 주차별 교육자료 추천
      // 백엔드로 전송할 데이터: weeklyContentFile.file_content (전체 weekly_content 데이터)
      // 이 데이터에는 모든 도메인의 weeklyContent가 포함되어 있어야 함
      const formData = new FormData();
      
      // weeklyContentFile.file_content가 없으면 에러
      if (!weeklyContentFile || !weeklyContentFile.file_content) {
        throw new Error('주차별 학습 내용 파일이 없습니다. 먼저 주차별 학습 내용을 생성해주세요.');
      }
      
      const dataToSend = weeklyContentFile.file_content;
      
      // 전송할 데이터 검증
      if (!dataToSend || typeof dataToSend !== 'object') {
        throw new Error('주차별 학습 내용 데이터 형식이 올바르지 않습니다.');
      }
      
      const weeklyContentBlob = new Blob([JSON.stringify(dataToSend, null, 2)], { type: 'application/json' });
      const weeklyContentFileForAPI = new File([weeklyContentBlob], 'weekly_content.json', { type: 'application/json' });
      
      // 디버깅: 전송할 데이터 확인
      console.log('백엔드로 전송할 데이터:', {
        dataToSend,
        keys: Object.keys(dataToSend),
        hasNumbersOperations: dataToSend?.numbersOperations_weeklyContent,
        numbersOperationsLength: dataToSend?.numbersOperations_weeklyContent?.length,
        numbersOperationsFirstItem: dataToSend?.numbersOperations_weeklyContent?.[0],
        hasReading: dataToSend?.reading_weeklyContent,
        readingLength: dataToSend?.reading_weeklyContent?.length
      });
      
      formData.append('iep_version_id', iepVersionId);
      formData.append('file_type', 'weekly_material'); // 백엔드는 "weekly_material" 사용
      formData.append('file', weeklyContentFileForAPI);

      const response = await fetch(`${API_BASE_URL}/iep-files`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // 에러 응답에서 상세 메시지 추출
        let errorMessage = 'AI 교육자료 추천에 실패했습니다.';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // JSON 파싱 실패 시 기본 메시지 사용
        }
        alert(`에러: ${errorMessage}`);
        throw new Error(errorMessage);
      }

      const createdFile = await response.json();
      
      // 생성된 파일 내용 로드
      const weeklyMaterialsContent = createdFile.file_content;
      
      // 백엔드 응답 형식 변환
      // 백엔드가 반환하는 형식: {domain_weekly_material: [{week: number, materials: [{title, url, keywords, file_type}]}, ...]}
      // domainKey는 위에서 이미 선언됨

      const materialKey = `${domainKey}_weekly_material`;
      
      // 백엔드 응답 형식에 맞게 URL 추출
      let recommendedMaterial: string[] = [];
      
      // 백엔드 응답에서 해당 도메인의 자료 찾기
      // 스펙 형식만 허용: {week: number, materials: [{title, url, keywords, file_type}]}
      if (!weeklyMaterialsContent || !weeklyMaterialsContent[materialKey] || !Array.isArray(weeklyMaterialsContent[materialKey])) {
        throw new Error(`백엔드 응답 형식 오류: ${materialKey} 데이터가 없거나 형식이 올바르지 않습니다.`);
      }

      // 주차별로 정렬하고 materials[0].title과 url 추출
      recommendedMaterial = weeklyMaterialsContent[materialKey]
        .sort((a: any, b: any) => (a.week || 0) - (b.week || 0))
        .map((item: any) => {
          // 스펙 형식만 허용: {week: number, materials: [{title, url, keywords, file_type}]}
          if (!item || !item.materials || !Array.isArray(item.materials) || item.materials.length === 0) {
            throw new Error(`백엔드 응답 형식 오류: week ${item?.week || 'unknown'}의 materials가 올바르지 않습니다.`);
          }
          const material = item.materials[0];
          const title = material.title || '';
          const url = material.url || '';
          
          // title이 있으면 "제목 - URL" 형식으로, 없으면 URL만 표시
          if (title && url) {
            return `${title} - ${url}`;
          } else if (title) {
            return title;
          } else if (url) {
            return url;
          }
          return '';
        });
      
      // 20주차가 아니면 빈 문자열로 채움
      while (recommendedMaterial.length < 20) {
        recommendedMaterial.push('');
      }
      recommendedMaterial = recommendedMaterial.slice(0, 20);
      
      const updatedMaterial = { ...weeklyMaterial, [materialKey]: recommendedMaterial };
      setWeeklyMaterial(updatedMaterial);
      setWeeklyMaterialFile(createdFile);
      
      // 백엔드에서 이미 올바른 형식으로 저장되었으므로 추가 저장 불필요
      alert('AI 교육자료 추천이 완료되었습니다.');
    } catch (err) {
      console.error('Error getting AI recommendations:', err);
      const errorMessage = err instanceof Error ? err.message : 'AI 추천을 가져오는데 실패했습니다.';
      alert(`에러: ${errorMessage}`);
      // 에러 발생 시 여기서 종료 (추가 처리 없음)
      return;
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

  // 교육자료 문자열에서 title과 url 파싱
  const parseMaterial = (materialStr: string): { title: string; url: string | null } => {
    if (!materialStr || !materialStr.trim()) {
      return { title: '', url: null };
    }
    
    // "제목 - URL" 형식인지 확인
    const parts = materialStr.split(' - ');
    if (parts.length >= 2) {
      const title = parts.slice(0, -1).join(' - '); // 마지막 부분 전까지가 title
      const url = parts[parts.length - 1]; // 마지막 부분이 URL
      // URL 형식인지 확인 (http:// 또는 https://로 시작)
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return { title: title.trim(), url: url.trim() };
      }
    }
    
    // URL만 있는 경우 (http:// 또는 https://로 시작)
    if (materialStr.startsWith('http://') || materialStr.startsWith('https://')) {
      return { title: materialStr, url: materialStr };
    }
    
    // title만 있는 경우
    return { title: materialStr, url: null };
  };

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
                            (() => {
                              const { title, url } = parseMaterial(material);
                              if (!title && !url) {
                                return <div className="plan-content-text">-</div>;
                              }
                              if (url) {
                                return (
                                  <div className="plan-content-text">
                                    <a 
                                      href={url} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="material-link"
                                    >
                                      {title || url}
                                    </a>
                                  </div>
                                );
                              }
                              return <div className="plan-content-text">{title}</div>;
                            })()
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

