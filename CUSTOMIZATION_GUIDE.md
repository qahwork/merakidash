# 🎨 프로젝트 커스터마이징 가이드

이 가이드는 Meraki Dashboard Pro를 자신의 회사에 맞게 커스터마이징하는 방법을 설명합니다.

## 📋 커스터마이징 가능한 항목들

### 1. **회사 브랜딩**
- 회사 로고
- 회사명
- 색상 테마
- 슬로건/태그라인

### 2. **로그인 시스템**
- 사용자명/비밀번호
- 로그인 페이지 디자인

### 3. **조직 관리**
- 기본 조직 설정
- 허용된 조직 목록
- 조직 필터링

### 4. **기타 설정**
- API 키
- 기본 시간 범위
- 기능 토글

## 🚀 커스터마이징 단계별 가이드

### **1단계: 프로젝트 클론 및 설정**

```bash
# GitHub에서 프로젝트 클론
git clone https://github.com/YOUR_USERNAME/meraki-dashboard-pro.git
cd meraki-dashboard-pro

# 설정 파일 생성
cp config_example.py config.py
```

### **2단계: 기본 설정 구성**

`config.py` 파일을 편집하여 기본 설정을 구성합니다:

```python
# =============================================
# 🔐 API CONFIGURATION
# =============================================

# Meraki API Key (필수)
MERAKI_API_KEY = "your_actual_meraki_api_key_here"

# =============================================
# 🔑 LOGIN CONFIGURATION
# =============================================

# 로그인 정보 (필수)
LOGIN_USERNAME = "your_username"  # 원하는 사용자명
LOGIN_PASSWORD = "your_secure_password"  # 안전한 비밀번호

# =============================================
# 🏢 ORGANIZATION CONFIGURATION
# =============================================

# 기본 조직 (선택사항)
DEFAULT_ORGANIZATION = "123456789012345678"  # 기본으로 선택할 조직 ID

# 허용된 조직 목록 (선택사항)
ALLOWED_ORGANIZATION_IDS = [
    "123456789012345678",  # 회사 A
    "987654321098765432",  # 회사 B
    "555666777888999000"   # 회사 C
]
```

### **3단계: 회사 로고 추가**

#### **3-1. 로고 파일 준비**
- 로고 파일을 프로젝트 루트에 추가
- 권장 크기: 150x150px (정사각형)
- 지원 형식: PNG, JPG, JPEG
- 파일명: `company_logo.png` (예시)

#### **3-2. 로고 파일 설정**
`config.py`에 로고 설정 추가:

```python
# =============================================
# 🎨 BRANDING CONFIGURATION
# =============================================

# 회사 로고 설정
COMPANY_LOGO_PATH = "company_logo.png"  # 로고 파일 경로
COMPANY_NAME = "Your Company Name"      # 회사명
COMPANY_TAGLINE = "Your Company Tagline"  # 슬로건 (선택사항)
COMPANY_COLOR = "#FF6B35"               # 회사 색상 (선택사항)
```

#### **3-3. 메인 파일 수정**
`meraki_dashboard_complete_final.py`에서 로고 표시 부분을 수정:

```python
# 로그인 페이지에서 (라인 390-403 근처)
def login_page():
    # ... 기존 코드 ...
    
    # 회사 로고 표시
    try:
        from config import COMPANY_LOGO_PATH, COMPANY_NAME, COMPANY_TAGLINE
        st.image(COMPANY_LOGO_PATH, width=150)
    except ImportError:
        # 기본 로고 또는 텍스트 로고
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;">
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: #1f2937; font-size: 2.5rem; font-weight: bold;">
                        🌐 Meraki Dashboard
                    </span>
                </div>
                <p style="color: #666; font-size: 0.9rem; margin: 0;">
                    Network Analytics & Management Platform
                </p>
            </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        # 로고 파일이 없을 때 텍스트 로고
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;">
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: #1f2937; font-size: 2.5rem; font-weight: bold;">
                        {COMPANY_NAME}
                    </span>
                </div>
                <p style="color: #666; font-size: 0.9rem; margin: 0;">
                    {COMPANY_TAGLINE}
                </p>
            </div>
        """, unsafe_allow_html=True)
```

### **4단계: 회사명 및 브랜딩 변경**

#### **4-1. 페이지 제목 변경**
`meraki_dashboard_complete_final.py`에서:

```python
# 페이지 설정 (라인 85-90)
st.set_page_config(
    page_title="Your Company Meraki Dashboard",  # 브라우저 탭 제목
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 제목 (라인 2329)
st.title("🌐 Your Company Meraki Dashboard")
```

#### **4-2. 사이드바 브랜딩 변경**
```python
# 사이드바 로고 (라인 454-464)
st.sidebar.markdown(f"""
<div style="text-align: center; margin-bottom: 1rem;">
    <span style="color: #1f2937; font-size: 1.8rem; font-weight: bold;">
        🌐 {COMPANY_NAME}
    </span>
    <p style="color: #666; margin: 0; font-size: 0.8rem;">
        {COMPANY_TAGLINE}
    </p>
</div>
""", unsafe_allow_html=True)
```

### **5단계: 색상 테마 커스터마이징**

#### **5-1. CSS 스타일 수정**
`meraki_dashboard_complete_final.py`의 CSS 부분에서:

```python
# 커스텀 CSS (라인 93 근처)
st.markdown(f"""
<style>
    /* 회사 색상 테마 */
    .main .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }}
    
    /* 회사 색상 적용 */
    .stButton > button {{
        background-color: {COMPANY_COLOR};
        color: white;
    }}
    
    .stButton > button:hover {{
        background-color: {COMPANY_COLOR}CC;
    }}
    
    /* 기타 스타일... */
</style>
""", unsafe_allow_html=True)
```

### **6단계: 조직 관리 설정**

#### **6-1. 조직 필터링 설정**
`config.py`에서:

```python
# 특정 조직만 표시하고 싶은 경우
ALLOWED_ORGANIZATION_IDS = [
    "601793500207386198",  # 본사
    "601793500207411804",  # 지사 1
    "601793500207414292"   # 지사 2
]

# 모든 조직을 표시하고 싶은 경우
ALLOWED_ORGANIZATION_IDS = None

# 기본 조직 설정
DEFAULT_ORGANIZATION = "601793500207386198"  # 기본으로 선택될 조직
```

### **7단계: 고급 커스터마이징**

#### **7-1. 로그인 페이지 완전 커스터마이징**
```python
def login_page():
    # 회사별 로그인 페이지 디자인
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {COMPANY_COLOR}, #ffffff);">
        <h1 style="color: white; margin-bottom: 1rem;">{COMPANY_NAME}</h1>
        <h2 style="color: #333;">Meraki Network Dashboard</h2>
        <p style="color: #666;">{COMPANY_TAGLINE}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그인 폼...
```

#### **7-2. 대시보드 헤더 커스터마이징**
```python
# 메인 대시보드 헤더
st.markdown(f"""
<div style="background: {COMPANY_COLOR}; color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
    <h1 style="margin: 0; color: white;">🌐 {COMPANY_NAME} Network Dashboard</h1>
    <p style="margin: 0.5rem 0 0 0; color: white;">{COMPANY_TAGLINE}</p>
</div>
""", unsafe_allow_html=True)
```

## 🔧 설정 파일 예시

### **완전한 config.py 예시**

```python
# =============================================
# 🔐 API CONFIGURATION
# =============================================
MERAKI_API_KEY = "your_actual_meraki_api_key_here"
API_RATE_LIMIT = 5
API_TIMEOUT = 30

# =============================================
# 🔑 LOGIN CONFIGURATION
# =============================================
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "your_secure_password_here"

# =============================================
# 🏢 ORGANIZATION CONFIGURATION
# =============================================
DEFAULT_ORGANIZATION = "123456789012345678"
ALLOWED_ORGANIZATION_IDS = [
    "123456789012345678",
    "987654321098765432"
]

# =============================================
# 🎨 BRANDING CONFIGURATION
# =============================================
COMPANY_LOGO_PATH = "company_logo.png"
COMPANY_NAME = "Your Company Name"
COMPANY_TAGLINE = "Your Company Tagline"
COMPANY_COLOR = "#FF6B35"

# =============================================
# 🎛️ DASHBOARD SETTINGS
# =============================================
DEFAULT_TIME_RANGE = "Last 24 hours"
DEFAULT_RESOLUTION = "5 minutes"
SHOW_DEBUG_INFO = False
```

## 📁 파일 구조

```
meraki-dashboard-pro/
├── config.py                  # ✅ 실제 설정 (Git 제외)
├── config_example.py          # ✅ 설정 템플릿
├── company_logo.png           # ✅ 회사 로고 (Git 제외)
├── meraki_dashboard_complete_final.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .gitignore                 # ✅ 민감한 파일들 제외
```

## 🚀 배포 방법

### **로컬 개발**
```bash
# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
cp config_example.py config.py
# config.py 편집

# 애플리케이션 실행
streamlit run meraki_dashboard_complete_final.py
```

### **Docker 배포**
```bash
# Docker 이미지 빌드
docker build -t meraki-dashboard .

# 컨테이너 실행
docker run -p 8501:8501 \
  -v $(pwd)/config.py:/app/config.py:ro \
  -v $(pwd)/company_logo.png:/app/company_logo.png:ro \
  meraki-dashboard
```

### **Docker Compose 배포**
```bash
# 서비스 시작
docker compose up -d

# 서비스 중지
docker compose down
```

## ⚠️ 주의사항

### **보안**
- `config.py`는 절대 Git에 커밋하지 마세요
- 로고 파일도 민감할 수 있으니 `.gitignore`에 추가하세요
- API 키와 비밀번호는 강력하게 설정하세요

### **파일 관리**
- 로고 파일은 적절한 크기로 최적화하세요
- 설정 변경 후에는 애플리케이션을 재시작하세요
- 백업을 정기적으로 수행하세요

## 🎉 완료!

이제 자신의 회사에 맞게 완전히 커스터마이징된 Meraki Dashboard를 사용할 수 있습니다!

### **체크리스트**
- [ ] API 키 설정
- [ ] 로그인 정보 설정
- [ ] 회사 로고 추가
- [ ] 회사명 변경
- [ ] 조직 ID 설정
- [ ] 색상 테마 적용
- [ ] 테스트 실행
- [ ] 배포 완료

**축하합니다! 🎉**
