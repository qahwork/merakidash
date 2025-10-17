# Meraki 웹훅 테스트 가이드

이 가이드는 Meraki 대시보드의 웹훅 기능을 테스트하는 방법을 설명합니다.

## 기본 테스트 방법

1. 대시보드 애플리케이션을 실행합니다:
   ```
   python meraki_dashboard_backup.py
   ```

2. 별도의 터미널에서 웹훅 테스트 도구를 사용합니다:
   ```
   python webhook_test_tool.py --url http://localhost:5000/webhook --secret your_webhook_secret_here
   ```

## 웹훅 테스트 도구 옵션

웹훅 테스트 도구는 다음과 같은 다양한 옵션을 제공합니다:

### 기본 옵션
- `--url`, `-u`: 웹훅 수신기 URL (필수)
- `--secret`, `-s`: 웹훅 검증을 위한 공유 비밀 키 (기본값: "your_webhook_secret_here")
- `--count`, `-c`: 전송할 웹훅 수 (기본값: 1)
- `--interval`, `-i`: 웹훅 전송 간격(초) (기본값: 1.0)

### 웹훅 내용 사용자 정의
- `--type`, `-t`: 알림 유형 ID (기본값: "test_alert")
- `--name`, `-n`: 알림 이름 (기본값: "Test Alert")
- `--level`, `-l`: 알림 수준 ["informational", "warning", "critical"] (기본값: "informational")
- `--device`, `-d`: 디바이스 이름 (기본값: "Test Device")
- `--network`, `-w`: 네트워크 이름 (기본값: "Test Network")
- `--data`, `-a`: 사용자 정의 알림 데이터 (JSON 형식)

### 연결 테스트
- `--test-connection`: 웹훅 엔드포인트 연결 테스트

## 테스트 예제

### 연결 테스트
```
python webhook_test_tool.py --url http://localhost:5000 --test-connection
```

### 중요(critical) 알림 보내기
```
python webhook_test_tool.py --url http://localhost:5000/webhook --level critical --name "테스트 중요 알림"
```

### 여러 테스트 이벤트 보내기
```
python webhook_test_tool.py --url http://localhost:5000/webhook --count 5 --interval 1.0
```

### 사용자 정의 알림 데이터 보내기
```
python webhook_test_tool.py --url http://localhost:5000/webhook --data '{"interface":"wan1", "status":"down", "details":"링크 다운 감지됨"}'
```

### 다양한 알림 유형 테스트
```
# 대역폭 초과 알림
python webhook_test_tool.py --url http://localhost:5000/webhook --type bw_threshold_exceeded --name "대역폭 임계값 초과" --level warning --data '{"interface":"wan1", "threshold":"80%", "usage":"85%"}'

# 장치 오프라인 알림
python webhook_test_tool.py --url http://localhost:5000/webhook --type device_offline --name "장치 오프라인" --level critical --data '{"lastSeen":"2023-09-29T15:30:00Z", "reason":"connection_lost"}'

# 보안 이벤트 알림
python webhook_test_tool.py --url http://localhost:5000/webhook --type security_event --name "보안 이벤트" --level critical --data '{"eventType":"intrusion", "sourceIP":"203.0.113.100", "destinationIP":"192.168.1.5"}'
```

## 웹훅 수신 확인

테스트 웹훅을 보낸 후 대시보드 애플리케이션에서 확인할 수 있습니다:

1. 웹훅 전용 탭: "📡 웹훅 이벤트" 탭으로 이동하여 수신된 이벤트를 확인합니다.

2. 통합 기능: 웹훅 데이터가 다음 페이지에 통합되어 표시됩니다:
   - "📊 개요" 탭: 웹훅 알림 인사이트 섹션에 주요 알림 요약 정보
   - "🚨 디바이스 상태 알림" 탭: 웹훅 알림 통합 디바이스 상태 섹션
   - "🌐 트래픽 분석" 탭: 트래픽 관련 알림 섹션

## 문제 해결

웹훅이 제대로 수신되지 않는 경우:

1. 웹훅 수신기가 실행 중인지 확인:
   - 대시보드 애플리케이션 시작 시 "웹훅 수신기가 시작되었습니다" 메시지를 확인

2. 공유 비밀 키가 올바른지 확인:
   - `config.py`의 `WEBHOOK_SECRET` 값과 테스트 도구의 `--secret` 옵션이 일치하는지 확인

3. 로컬 네트워크 설정 확인:
   - 방화벽이나 보안 소프트웨어가 웹훅 수신을 차단하지 않는지 확인

4. 디버그 정보 활성화:
   - `config.py`에서 `SHOW_DEBUG_INFO = True`로 설정하여 자세한 오류 정보 확인


