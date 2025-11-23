FROM node:25-alpine3.21

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 소스 코드 복사
COPY . .

# 개발 서버 포트 노출
EXPOSE 5173

# 개발 서버 실행 (핫 리로드 지원)
CMD ["npm", "run", "dev", "--", "--host"]