# 🪟 Windows에서 Meraki Dashboard 빠른 시작 가이드

이 문서는 Windows PC에서 Meraki Network Analytics Dashboard Pro를 빠르게 실행하는 방법을 설명합니다.

## 🚀 **가장 간단한 실행 방법**

### **방법 1: 배치 파일 사용 (권장)**
1. **`start_dashboard.bat` 파일을 더블클릭**
2. 자동으로 Python 설치 확인, 가상환경 생성, 패키지 설치, 대시보드 실행
3. 웹 브라우저에서 `http://localhost:8501` 접속

### **방법 2: PowerShell 스크립트 사용**
```powershell
# PowerShell에서 실행
.\start_dashboard.ps1

# 또는 특정 포트로 실행
.\start_dashboard.ps1 -Port 8502
```

### **방법 3: 수동 실행**
```cmd
# 명령 프롬프트에서 실행
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run meraki_dashboard_complete_final.py
```

## 📋 **사전 요구사항**

### **Python 설치 (한 번만)**
1. [Python 공식 사이트](https://www.python.org/downloads/) 방문
2. **Python 3.8 이상** 다운로드
3. 설치 시 **"Add Python to PATH"** 체크박스 **반드시 선택**
4. 설치 완료 후 컴퓨터 재시작

### **설치 확인**
```cmd
python --version
pip --version
```

## 🔧 **자동 실행 스크립트 설명**

### **start_dashboard.bat (배치 파일)**
- ✅ Python 설치 자동 확인
- ✅ 가상환경 자동 생성
- ✅ 필요한 패키지 자동 설치
- ✅ 대시보드 자동 실행
- ✅ 오류 발생 시 해결 방법 안내

### **start_dashboard.ps1 (PowerShell)**
- ✅ 배치 파일과 동일한 기능
- ✅ 더 나은 오류 처리
- ✅ 포트 번호 커스터마이징 가능
- ✅ 색상 있는 출력

## 📁 **프로젝트 구조**
```
merakitest/
├── start_dashboard.bat          # 🚀 Windows 배치 파일 (더블클릭으로 실행)
├── start_dashboard.ps1          # 🔧 PowerShell 스크립트
├── meraki_dashboard_complete_final.py  # 📊 메인 대시보드
├── config.py                    # ⚙️ 설정 파일
├── requirements.txt             # 📦 Python 패키지 목록
├── run_dashboard.py             # 🐍 Python 실행 스크립트
└── WINDOWS_QUICK_START.md      # 📖 이 가이드
```

## 🎯 **실행 단계별 과정**

### **1단계: 파일 준비**
- 프로젝트 폴더를 USB나 클라우드로 복사
- 대상 Windows PC에 붙여넣기

### **2단계: Python 설치 (최초 1회)**
- Python 3.8+ 다운로드 및 설치
- "Add Python to PATH" 체크박스 선택

### **3단계: 대시보드 실행**
- `start_dashboard.bat` 더블클릭
- 자동으로 모든 설정 완료
- 웹 브라우저에서 대시보드 접속

## 🌐 **대시보드 접속**

### **로컬 접속**
- **URL**: `http://localhost:8501`
- **또는**: `http://127.0.0.1:8501`

### **네트워크 접속 (다른 PC에서)**
- **URL**: `http://[현재PC_IP]:8501`
- **예시**: `http://192.168.1.100:8501`

## 🔐 **초기 설정**

### **Meraki API 키 입력**
1. 사이드바에서 "Meraki API Key" 입력
2. [Meraki Dashboard](https://dashboard.meraki.com)에서 API 키 생성
3. Organization > Settings > API access

### **Demo 모드 사용**
1. 사이드바에서 "Demo Mode" 체크박스 선택
2. 실제 하드웨어 없이 모든 기능 테스트 가능

## 🚨 **문제 해결**

### **Python이 인식되지 않는 경우**
```cmd
# 환경 변수 확인
echo %PATH%

# Python 경로 직접 지정
C:\Users\[사용자명]\AppData\Local\Programs\Python\Python39\python.exe
```

### **포트 8501이 사용 중인 경우**
```cmd
# 다른 포트로 실행
streamlit run meraki_dashboard_complete_final.py --server.port 8502
```

### **패키지 설치 오류**
```cmd
# pip 업그레이드
python -m pip install --upgrade pip

# 가상환경 재생성
rmdir /s venv
python -m venv venv
```

### **방화벽 경고**
- Windows 방화벽에서 "액세스 허용" 선택
- 또는 방화벽에서 Python과 Streamlit 허용

## 📱 **모바일 접속**

### **같은 Wi-Fi 네트워크에서**
1. Windows PC의 IP 주소 확인: `ipconfig`
2. 모바일 브라우저에서 `http://[PC_IP]:8501` 접속

### **외부에서 접속**
- 포트 포워딩 설정 필요
- 보안상 권장하지 않음

## 🔄 **업데이트 방법**

### **코드 업데이트**
```cmd
# Git 사용 시
git pull origin main

# 수동 업데이트 시
# 새 파일로 교체 후 재실행
```

### **패키지 업데이트**
```cmd
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

## 💡 **팁과 트릭**

### **빠른 실행**
- `start_dashboard.bat`를 바탕화면에 바로가기 생성
- Windows 시작 프로그램에 추가하여 자동 실행

### **성능 최적화**
- 가상환경을 SSD에 생성
- 불필요한 백그라운드 프로그램 종료

### **백업**
- `config.py` 파일 백업 (API 키 포함)
- 전체 프로젝트 폴더 압축하여 보관

---

## 🎉 **축하합니다!**

이제 Windows에서 Meraki Dashboard를 쉽게 실행할 수 있습니다!

**🚀 빠른 시작**: `start_dashboard.bat` 더블클릭만 하면 됩니다!

**📞 문제 발생 시**: 
1. 이 가이드의 문제 해결 섹션 확인
2. Python 설치 상태 점검
3. 방화벽 설정 확인
