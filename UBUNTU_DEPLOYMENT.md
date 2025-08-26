# 🐧 Ubuntu 서버 배포 가이드

이 문서는 Ubuntu 서버에서 Meraki Network Analytics Dashboard Pro를 배포하는 방법을 설명합니다.

## 📋 시스템 요구사항

### 최소 요구사항
- **OS**: Ubuntu 20.04 LTS 이상
- **RAM**: 2GB 이상 (4GB 권장)
- **Storage**: 10GB 이상의 여유 공간
- **CPU**: 2코어 이상
- **Network**: 인터넷 연결 및 80/443 포트 접근 가능

### 권장 사양
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **CPU**: 4코어
- **Network**: 고정 IP 주소

## 🚀 빠른 설치 (자동화 스크립트)

### 1. 프로젝트 다운로드
```bash
# 프로젝트 클론
git clone <your-repository-url>
cd merakitest

# 설치 스크립트 실행 권한 부여
chmod +x install_ubuntu.sh

# 설치 스크립트 실행
./install_ubuntu.sh
```

### 2. 설정 파일 편집
```bash
# 설정 파일 편집
nano ~/meraki-dashboard/config.py

# Meraki API 키 입력
MERAKI_API_KEY = "your_actual_api_key_here"
```

### 3. 서비스 상태 확인
```bash
# 상태 확인
./check_status.sh

# 로그 확인
sudo journalctl -u meraki-dashboard -f
```

## 🔧 수동 설치 (단계별)

### 1. 시스템 업데이트
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 필수 패키지 설치
```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    wget \
    nginx \
    supervisor \
    ufw
```

### 3. 프로젝트 설정
```bash
# 프로젝트 디렉토리 생성
mkdir -p ~/meraki-dashboard
cd ~/meraki-dashboard

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 4. Streamlit 설정
```bash
# Streamlit 설정 파일 생성
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
EOF
```

### 5. Systemd 서비스 생성
```bash
sudo tee /etc/systemd/system/meraki-dashboard.service > /dev/null << EOF
[Unit]
Description=Meraki Network Analytics Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/meraki-dashboard
Environment=PATH=$HOME/meraki-dashboard/venv/bin
ExecStart=$HOME/meraki-dashboard/venv/bin/streamlit run meraki_dashboard_complete_final.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable meraki-dashboard
sudo systemctl start meraki-dashboard
```

### 6. Nginx 설정
```bash
# Nginx 설정 파일 생성
sudo tee /etc/nginx/sites-available/meraki-dashboard > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

# 사이트 활성화
sudo ln -sf /etc/nginx/sites-available/meraki-dashboard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 설정 테스트 및 재시작
sudo nginx -t
sudo systemctl restart nginx
```

### 7. 방화벽 설정
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
```

## 🐳 Docker를 사용한 배포

### 1. Docker 및 Docker Compose 설치
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 새 터미널 세션 시작 또는 재로그인
newgrp docker
```

### 2. Docker Compose로 배포
```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 상태 확인
docker-compose ps
```

## 🔐 SSL 인증서 설정 (Let's Encrypt)

### 1. Certbot 설치
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. SSL 인증서 발급
```bash
# 도메인이 있는 경우
sudo certbot --nginx -d yourdomain.com

# 도메인이 없는 경우 (자체 서명 인증서)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt
```

## 📊 모니터링 및 유지보수

### 1. 서비스 상태 확인
```bash
# Dashboard 서비스 상태
sudo systemctl status meraki-dashboard

# Nginx 상태
sudo systemctl status nginx

# 포트 사용 현황
sudo netstat -tlnp | grep :8501
```

### 2. 로그 확인
```bash
# Dashboard 로그
sudo journalctl -u meraki-dashboard -f

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 3. 성능 모니터링
```bash
# 시스템 리소스 사용량
htop

# 디스크 사용량
df -h

# 메모리 사용량
free -h
```

## 🚨 문제 해결

### 일반적인 문제들

#### 1. 포트 8501이 열리지 않는 경우
```bash
# 방화벽 확인
sudo ufw status

# 포트 열기
sudo ufw allow 8501/tcp
```

#### 2. Streamlit이 시작되지 않는 경우
```bash
# 가상환경 활성화 확인
source ~/meraki-dashboard/venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl restart meraki-dashboard
```

#### 3. Nginx 연결 오류
```bash
# Nginx 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx

# 포트 사용 현황 확인
sudo netstat -tlnp | grep :80
```

## 📈 성능 최적화

### 1. Streamlit 설정 최적화
```bash
# ~/.streamlit/config.toml에 추가
[server]
maxUploadSize = 200
maxMessageSize = 200
```

### 2. Nginx 성능 튜닝
```bash
# /etc/nginx/nginx.conf에 추가
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### 3. 시스템 최적화
```bash
# 스왑 파일 생성 (메모리 부족 시)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🔄 업데이트 및 백업

### 1. 코드 업데이트
```bash
cd ~/meraki-dashboard
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart meraki-dashboard
```

### 2. 백업
```bash
# 설정 파일 백업
cp ~/meraki-dashboard/config.py ~/backup_config.py

# 전체 프로젝트 백업
tar -czf ~/meraki-dashboard-backup-$(date +%Y%m%d).tar.gz ~/meraki-dashboard
```

## 📞 지원 및 문의

문제가 발생하거나 추가 도움이 필요한 경우:
1. 로그 파일 확인
2. 시스템 상태 점검
3. GitHub Issues에 문제 보고

---

**🎉 축하합니다! 이제 Ubuntu 서버에서 Meraki Dashboard가 실행되고 있습니다.**
