# 🚀 빠른 시작 가이드

Meraki Dashboard Pro를 5분 안에 설정하고 실행하는 방법입니다.

## 📋 사전 준비사항

- Python 3.8+ 설치
- Meraki API 키
- Git 설치 (선택사항)

## ⚡ 5분 설정

### **1단계: 프로젝트 다운로드**

```bash
# GitHub에서 클론
git clone https://github.com/YOUR_USERNAME/meraki-dashboard-pro.git
cd meraki-dashboard-pro

# 또는 ZIP 파일 다운로드 후 압축 해제
```

### **2단계: 의존성 설치**

```bash
# Python 패키지 설치
pip install -r requirements.txt
```

### **3단계: 설정 파일 생성**

```bash
# 설정 템플릿 복사
cp config_example.py config.py
```

### **4단계: 기본 설정**

`config.py` 파일을 열고 다음 정보를 입력하세요:

```python
# 필수 설정
MERAKI_API_KEY = "your_actual_meraki_api_key_here"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "your_secure_password"

# 선택 설정 (회사 정보)
COMPANY_NAME = "Your Company Name"
COMPANY_LOGO_PATH = "company_logo.png"  # 로고 파일이 있다면
```

### **5단계: 실행**

```bash
# 애플리케이션 실행
streamlit run meraki_dashboard_complete_final.py
```

## 🌐 접속

브라우저에서 `http://localhost:8501`로 접속하세요.

## 🎨 커스터마이징 (선택사항)

### **회사 로고 추가**
1. 로고 파일을 프로젝트 루트에 `company_logo.png`로 저장
2. `config.py`에서 `COMPANY_LOGO_PATH = "company_logo.png"` 설정

### **조직 필터링**
```python
# config.py에서
ALLOWED_ORGANIZATION_IDS = [
    "your_org_id_1",
    "your_org_id_2"
]
```

## 🐳 Docker로 실행 (고급)

```bash
# Docker 이미지 빌드
docker build -t meraki-dashboard .

# 컨테이너 실행
docker run -p 8501:8501 \
  -v $(pwd)/config.py:/app/config.py:ro \
  meraki-dashboard
```

## ❓ 문제 해결

### **API 키 오류**
- Meraki Dashboard에서 API 키가 활성화되어 있는지 확인
- API 키에 적절한 권한이 있는지 확인

### **로그인 실패**
- `config.py`의 `LOGIN_USERNAME`과 `LOGIN_PASSWORD` 확인
- 설정 파일이 올바른 위치에 있는지 확인

### **조직이 보이지 않음**
- `ALLOWED_ORGANIZATION_IDS`를 `None`으로 설정하여 모든 조직 표시
- API 키에 조직 접근 권한이 있는지 확인

## 📚 더 자세한 정보

- **전체 설정**: [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)
- **배포 가이드**: [GITHUB_DEPLOYMENT_GUIDE.md](GITHUB_DEPLOYMENT_GUIDE.md)
- **보안 가이드**: [SECURITY_AUDIT.md](SECURITY_AUDIT.md)

## 🎉 완료!

축하합니다! 이제 Meraki Dashboard를 사용할 수 있습니다.

**다음 단계:**
1. 회사 정보 커스터마이징
2. 조직 설정
3. 프로덕션 배포

**도움이 필요하시면 이슈를 생성해 주세요!** 🚀
