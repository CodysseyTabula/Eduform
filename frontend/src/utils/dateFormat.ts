/**
 * YYYY-MM-DD 형식의 날짜를 'YYYY년 M월 D일 생' 형식으로 변환
 * 한자리 숫자는 0을 붙이지 않음
 */
export const formatBirthDate = (dateString: string): string => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = date.getMonth() + 1; // getMonth()는 0부터 시작
  const day = date.getDate();
  
  return `${year}년 ${month}월 ${day}일 생`;
};

