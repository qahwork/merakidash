# 🚀 GitHub 배포 가이드 - Meraki Dashboard Pro

이 가이드는 Meraki Network Analytics Dashboard Pro를 GitHub에 업로드하고 우분투 서버에 배포하는 방법을 설명합니다.

## 📋 사전 준비사항

### 1. GitHub 계정 및 저장소
- [GitHub](https://github.com) 계정 생성
- 새 저장소 생성 (예: `meraki-dashboard-pro`)

### 2. 로컬 환경
- Git 설치
- Docker 및 Docker Compose 설치 (우분투 서버용)

## 🔧 GitHub 업로드 단계

### 1단계: Git 저장소 초기화

```bash
# 프로젝트 디렉토리에서
git init

# 원격 저장소 추가 (YOUR_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 기본 브랜치 설정
git branch -M main
```

### 2단계: 파일 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 첫 번째 커밋
git commit -m "Initial commit: Meraki Dashboard Pro v1.0.0"

# GitHub에 푸시
git push -u origin main
```

### 3단계: .gitignore 확인

다음 파일들이 제외되는지 확인:
- `config.py` (민감한 API 키 포함)
- `logs/` 디렉토리
- `__pycache__/` 디렉토리
- `.env` 파일들

## 🐧 우분투 서버 배포

### 1단계: 서버 준비

```bash
# 우분투 서버에 SSH 접속
ssh username@your-server-ip

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필요한 패키지 설치
sudo apt install -y git curl wget
```

### 2단계: 프로젝트 클론

```bash
# 프로젝트 클론
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# 배포 스크립트 실행 권한 부여
chmod +x deploy_ubuntu.sh
```

### 3단계: 자동 배포 실행

```bash
# 자동 배포 스크립트 실행
./deploy_ubuntu.sh
```

### 4단계: 수동 배포 (선택사항)

자동 배포 스크립트를 사용하지 않는 경우:

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo apt install -y docker-compose-plugin

# 설정 파일 생성
cp config_example.py config.py
nano config.py  # API 키 설정

# 컨테이너 빌드 및 실행
docker compose up -d
```

## ⚙️ 설정 및 구성

### 1. API 키 설정

```bash
# 설정 파일 편집
nano config.py

# 다음 값들을 설정:
MERAKI_API_KEY = "your_actual_meraki_api_key_here"
```

### 2. 방화벽 설정

```bash
# UFW 방화벽 설정
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8501/tcp
sudo ufw enable
```

### 3. SSL 인증서 설정 (선택사항)

```bash
# Let's Encrypt 인증서 설치
sudo apt install -y certbot

# 인증서 발급 (도메인이 있는 경우)
sudo certbot certonly --standalone -d your-domain.com

# 인증서를 ssl/ 디렉토리로 복사
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/
```

## 🔍 서비스 관리

### Docker Compose 명령어

```bash
# 서비스 시작
docker compose up -d

# 서비스 중지
docker compose down

# 서비스 재시작
docker compose restart

# 로그 확인
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f meraki-dashboard
```

### 시스템 서비스 관리

```bash
# 서비스 시작
sudo systemctl start meraki-dashboard

# 서비스 중지
sudo systemctl stop meraki-dashboard

# 서비스 상태 확인
sudo systemctl status meraki-dashboard

# 서비스 자동 시작 설정
sudo systemctl enable meraki-dashboard
```

## 📊 모니터링 및 로그

### 1. 컨테이너 상태 확인

```bash
# 실행 중인 컨테이너 확인
docker compose ps

# 리소스 사용량 확인
docker stats
```

### 2. 로그 확인

```bash
# 애플리케이션 로그
tail -f logs/dashboard.log

# Docker 로그
docker compose logs -f meraki-dashboard

# Nginx 로그
docker compose logs -f nginx
```

### 3. 헬스 체크

```bash
# 애플리케이션 헬스 체크
curl http://localhost:8501/_stcore/health

# Nginx 헬스 체크
curl http://localhost/health
```

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 확인
sudo netstat -tlnp | grep :8501

# 프로세스 종료
sudo kill -9 PID
```

#### 2. 권한 문제
```bash
# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER

# 로그아웃 후 재로그인
```

#### 3. 메모리 부족
```bash
# 메모리 사용량 확인
free -h

# Docker 리소스 제한 확인
docker stats
```

#### 4. API 연결 문제
```bash
# API 키 확인
grep MERAKI_API_KEY config.py

# 네트워크 연결 확인
curl -I https://api.meraki.com
```

## 🚀 고급 설정

### 1. Nginx 리버스 프록시 설정

```bash
# Nginx 설정 파일 편집
nano nginx.conf

# SSL 리다이렉트 설정
# HTTPS 강제 사용
# Gzip 압축 설정
```

### 2. 자동 백업 설정

```bash
# 백업 스크립트 생성
nano backup.sh

# crontab에 백업 작업 추가
crontab -e
# 0 2 * * * /path/to/backup.sh
```

### 3. 모니터링 설정

```bash
# Prometheus + Grafana 설정
# 또는 간단한 모니터링 스크립트
```

## 📞 지원 및 문의

### 문제 발생 시

1. **로그 확인**: `docker compose logs -f`
2. **상태 확인**: `docker compose ps`
3. **리소스 확인**: `docker stats`
4. **네트워크 확인**: `curl -I http://localhost:8501`

### 유용한 명령어

```bash
# 전체 시스템 상태
docker compose ps && docker stats --no-stream

# 로그 실시간 모니터링
docker compose logs -f --tail=100

# 컨테이너 재빌드
docker compose build --no-cache && docker compose up -d

# 볼륨 정리
docker system prune -a
```

---

## 🎉 배포 완료!

배포가 완료되면 다음 URL로 접속할 수 있습니다:

- **메인 대시보드**: `http://your-server-ip:8501`
- **Nginx 프록시**: `http://your-server-ip` (포트 80)
- **HTTPS**: `https://your-domain.com` (SSL 설정 시)

**축하합니다! Meraki Dashboard Pro가 성공적으로 배포되었습니다!** 🚀
