/**
 * 더미 학생 데이터
 * 백엔드 API 연결 전 개발용으로 사용
 * 백엔드 연결 후 이 파일과 api.ts의 USE_MOCK_DATA 플래그를 제거하면 됩니다.
 */

import type { Student } from '../utils/api';

export const mockStudents: Student[] = [
  {
    id: '1',
    name: '김철수',
    birth: '2010-03-15'
  },
  {
    id: '2',
    name: '이영희',
    birth: '2011-07-22'
  },
  {
    id: '3',
    name: '박민수',
    birth: '2009-11-08'
  },
  {
    id: '4',
    name: '최지은',
    birth: '2012-01-30'
  },
  {
    id: '5',
    name: '정동현',
    birth: '2010-09-14'
  }
];

