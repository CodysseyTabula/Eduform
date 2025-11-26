// TODO: 백엔드 연결 후 이 플래그를 false로 변경하거나 제거하세요
const USE_MOCK_DATA = true;

const API_BASE_URL = 'http://localhost:8000'; // 백엔드 URL (필요시 환경변수로 변경)

export interface Student {
  id: string;
  name: string;
  birth: string; // YYYY-MM-DD 형식
}

export interface CreateStudentRequest {
  name: string;
  birth: string; // YYYY-MM-DD 형식
}

export interface CreateStudentResponse {
  id: string;
  name: string;
  birth: string;
}

// 더미 데이터 저장소 (메모리 기반)
let mockStudentsStore: Student[] = [];

/**
 * 모든 학생 목록 조회
 */
export const getStudents = async (): Promise<Student[]> => {
  if (USE_MOCK_DATA) {
    // 더미 데이터 사용
    const { mockStudents } = await import('../data/mockStudents');
    // 초기 로드 시 더미 데이터로 초기화
    if (mockStudentsStore.length === 0) {
      mockStudentsStore = [...mockStudents];
    }
    // 약간의 지연을 추가하여 실제 API 호출처럼 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 300));
    return [...mockStudentsStore];
  }

  // 실제 API 호출
  const response = await fetch(`${API_BASE_URL}/students`);
  if (!response.ok) {
    throw new Error('학생 목록을 불러오는데 실패했습니다.');
  }
  return response.json();
};

/**
 * 새 학생 추가
 */
export const createStudent = async (
  data: CreateStudentRequest
): Promise<CreateStudentResponse> => {
  if (USE_MOCK_DATA) {
    // 더미 데이터 사용
    const newStudent: Student = {
      id: `mock-${Date.now()}`, // 간단한 ID 생성
      name: data.name,
      birth: data.birth,
    };
    mockStudentsStore.push(newStudent);
    // 약간의 지연을 추가하여 실제 API 호출처럼 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 300));
    return newStudent;
  }

  // 실제 API 호출
  const response = await fetch(`${API_BASE_URL}/students`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error('학생 추가에 실패했습니다.');
  }
  
  return response.json();
};

// IEP 관련 타입 및 API

export interface IEPVersion {
  id: string;
  student_id: string;
  year: string;
  semester: string;
  grade: string;
  created_at: string; // ISO8601
}

export interface CreateIEPVersionRequest {
  student_id: string;
  year: string; // 예: "2025"
  semester: string;
  grade: string;
}

export interface CreateIEPVersionResponse {
  id: string;
  student_id: string;
  year: string;
  semester: string;
  grade: string;
  created_at: string; // ISO8601
}

/**
 * IEP 버전 생성
 */
export const createIEPVersion = async (
  data: CreateIEPVersionRequest
): Promise<CreateIEPVersionResponse> => {
  if (USE_MOCK_DATA) {
    // 더미 데이터 사용 (나중에 제거)
    const newIEP: IEPVersion = {
      id: `mock-iep-${Date.now()}`,
      student_id: data.student_id,
      year: data.year,
      semester: data.semester,
      grade: data.grade,
      created_at: new Date().toISOString(),
    };
    await new Promise(resolve => setTimeout(resolve, 300));
    return newIEP;
  }

  const response = await fetch(`${API_BASE_URL}/iep-versions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error('IEP 버전 생성에 실패했습니다.');
  }
  
  return response.json();
};

/**
 * 학생 최신 IEP 조회
 */
export const getLatestIEP = async (studentId: string): Promise<IEPVersion> => {
  if (USE_MOCK_DATA) {
    // 더미 데이터 사용 (나중에 제거)
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      id: `mock-iep-latest-${studentId}`,
      student_id: studentId,
      year: '2025',
      semester: '1',
      grade: '3',
      created_at: new Date().toISOString(),
    };
  }

  const response = await fetch(`${API_BASE_URL}/students/${studentId}/iep-latest`);
  if (!response.ok) {
    throw new Error('최신 IEP를 불러오는데 실패했습니다.');
  }
  return response.json();
};

/**
 * 학생 IEP 목록 조회
 */
export const getIEPVersions = async (studentId: string): Promise<Omit<IEPVersion, 'student_id'>[]> => {
  if (USE_MOCK_DATA) {
    // 더미 데이터 사용 (나중에 제거)
    await new Promise(resolve => setTimeout(resolve, 300));
    return [
      {
        id: `mock-iep-1-${studentId}`,
        year: '2025',
        semester: '1',
        grade: '3',
        created_at: new Date().toISOString(),
      },
      {
        id: `mock-iep-2-${studentId}`,
        year: '2024',
        semester: '2',
        grade: '2',
        created_at: new Date(Date.now() - 86400000).toISOString(),
      },
    ];
  }

  const response = await fetch(`${API_BASE_URL}/students/${studentId}/iep-versions`);
  if (!response.ok) {
    throw new Error('IEP 목록을 불러오는데 실패했습니다.');
  }
  return response.json();
};

