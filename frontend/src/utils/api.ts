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

/**
 * 모든 학생 목록 조회
 */
export const getStudents = async (): Promise<Student[]> => {
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
  const response = await fetch(`${API_BASE_URL}/students/${studentId}/iep-versions`);
  if (!response.ok) {
    throw new Error('IEP 목록을 불러오는데 실패했습니다.');
  }
  return response.json();
};

export interface IEPFile {
  id: string;
  file_type: string;
  file_path: string;
  updated_at: string; // ISO8601
}

export interface CreateIEPFileRequest {
  iep_version_id: string;
  file_type: string;
  file: File;
}

export interface CreateIEPFileResponse {
  id: string;
  iep_version_id: string;
  file_type: string;
  file_path: string;
  updated_at: string; // ISO8601
}

export interface UpdateIEPFileRequest {
  file: File;
}

export interface UpdateIEPFileResponse {
  id: string;
  iep_version_id: string;
  file_type: string;
  file_path: string;
  updated_at: string; // ISO8601
}

/**
 * IEP 파일 목록 조회
 */
export const getIEPFiles = async (iepVersionId: string): Promise<IEPFile[]> => {
  const response = await fetch(`${API_BASE_URL}/iep-versions/${iepVersionId}/iep-files`);
  if (!response.ok) {
    throw new Error('IEP 파일 목록을 불러오는데 실패했습니다.');
  }
  return response.json();
};

/**
 * IEP 파일 생성 (처음 생성)
 */
export const createIEPFile = async (
  data: CreateIEPFileRequest
): Promise<CreateIEPFileResponse> => {
  const formData = new FormData();
  formData.append('iep_version_id', data.iep_version_id);
  formData.append('file_type', data.file_type);
  formData.append('file', data.file);

  const response = await fetch(`${API_BASE_URL}/iep-files`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('IEP 파일 생성에 실패했습니다.');
  }
  
  return response.json();
};

/**
 * IEP 파일 수정 (기존 파일 수정)
 */
export const updateIEPFile = async (
  fileId: string,
  data: UpdateIEPFileRequest
): Promise<UpdateIEPFileResponse> => {
  const formData = new FormData();
  formData.append('file', data.file);

  const response = await fetch(`${API_BASE_URL}/iep-files/${fileId}`, {
    method: 'PUT',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('IEP 파일 수정에 실패했습니다.');
  }
  
  return response.json();
};

/**
 * IEP JSON 파일 내용 조회
 * filePath는 백엔드에서 반환된 절대 경로 또는 상대 경로입니다.
 * 백엔드가 정적 파일을 제공하는 경우 filePath를 그대로 사용하고,
 * 그렇지 않은 경우 /iep-files/{file_id}/content 엔드포인트를 사용할 수 있습니다.
 */
export const getIEPFileContent = async (filePath: string): Promise<any> => {
  // filePath가 절대 경로인 경우 그대로 사용, 상대 경로인 경우 API_BASE_URL과 결합
  const url = filePath.startsWith('http') 
    ? filePath 
    : filePath.startsWith('/') 
      ? `${API_BASE_URL}${filePath}`
      : `${API_BASE_URL}/${filePath}`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('IEP 파일 내용을 불러오는데 실패했습니다.');
  }
  return response.json();
};

/**
 * 워드 파일 다운로드
 */
export const downloadIEPDocx = async (iepVersionId: string): Promise<Blob> => {
  const response = await fetch(`${API_BASE_URL}/iep-versions/${iepVersionId}/docx`);
  if (!response.ok) {
    throw new Error('워드 파일 다운로드에 실패했습니다.');
  }
  return response.blob();
};

