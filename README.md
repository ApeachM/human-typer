# Human Typer

사람이 타이핑하는 것처럼 자연스러운 속도로 텍스트를 입력해주는 PyQt5 GUI 도구입니다. 데모, 녹화, 또는 자연스러운 타이핑이 필요한 모든 상황에서 사용할 수 있습니다.

## 주요 기능

- **Human-like 타이핑**: 키 입력 사이에 랜덤 딜레이로 자연스러운 타이핑 구현
- **한글 지원**: 한글을 포함한 모든 유니코드 문자 지원
- **속도 조절**: 최소/최대 타이핑 딜레이 설정 가능
- **창 자동 선택**: 타이핑할 대상 창을 자동 감지하고 선택
- **일시정지 & 재개**: 타이핑 중단 후 이어서 진행 가능
- **크로스 플랫폼**: Windows, macOS, Linux 지원

## 설치 및 실행

### 간편 실행 (권장)

**Linux/macOS:**
```bash
./run_human_typer.sh
```

**Windows:**
```cmd
run_human_typer.bat
```

실행 스크립트가 자동으로:
1. 가상 환경 생성
2. 의존성 설치
3. 애플리케이션 실행

### 수동 설치

```bash
# 가상 환경 생성
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 또는
.venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 실행
python human_typer.py
# 또는
python -m human_typer
```

## 의존성

- Python 3.10+
- PyQt5
- pyautogui
- pyperclip

### Linux 추가 요구사항

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-dev

# RHEL/CentOS/Fedora
sudo dnf install python3-tkinter python3-devel
# Python 3.12인 경우:
sudo dnf install python3.12-tkinter

# 창 전환 기능을 위해 (선택사항)
sudo dnf install wmctrl  # 또는 xdotool
```

## 사용법

### GUI 모드

1. **텍스트 입력**: 타이핑할 텍스트를 텍스트 영역에 붙여넣기
2. **대상 창 선택**:
   - 타이핑할 창을 클릭하면 "Detected"에 창 이름이 표시됨
   - (선택) "Fix" 버튼으로 대상 창 고정
3. **설정 조정**:
   - **Min Delay (ms)**: 키 입력 간 최소 딜레이 (기본값: 40ms)
   - **Max Delay (ms)**: 키 입력 간 최대 딜레이 (기본값: 100ms)
4. **Start 클릭**: Start 버튼 클릭 또는 `Ctrl+Enter`
5. **자동 타이핑**: 대상 창이 자동 활성화되고 타이핑 시작

#### 버튼 및 단축키

| 버튼 | 단축키 | 기능 |
|------|--------|------|
| Start | `Ctrl+Enter` | 타이핑 시작 (일시정지 상태면 재개) |
| Stop | - | 현재 위치에서 일시정지 |
| Fix | - | 감지된 창을 대상으로 고정 |
| Clear | - | 고정된 창 선택 해제 |

### CLI 모드

```bash
# 도움말
python human_typer.py --help

# 파일에서 읽어서 타이핑 (3초 카운트다운 후)
python human_typer.py -f input.txt

# 텍스트 직접 입력
python human_typer.py -t "Hello World"

# stdin에서 읽기
echo "print('hello')" | python human_typer.py --stdin

# 속도 조절 (느린 타이핑)
python human_typer.py -f input.txt --min-delay 100 --max-delay 200

# 카운트다운 없이 즉시 시작
python human_typer.py -f input.txt -c 0
```

### 창 전환 기능

특정 창으로 자동 포커스 후 타이핑할 수 있습니다.

```bash
# 사용 가능한 창 목록 보기
python human_typer.py --list-windows

# 특정 창에 타이핑 (부분 매칭 지원)
python human_typer.py -f input.txt --window "Notepad"
python human_typer.py -f input.txt --window "Visual Studio Code"
python human_typer.py -f input.txt -w "Chrome"  # 부분 매칭
```

**창 제목 매칭:**
- 정확한 매칭 먼저 시도
- 없으면 부분 매칭 (대소문자 무시)
- 예: `--window "Code"` → "Visual Studio Code" 매칭

### Watch 모드 (자동화용)

Claude나 다른 자동화 도구에서 사용하기 위한 모드입니다.
특정 파일을 감시하다가, 파일이 생성되면 그 내용을 타이핑합니다.

```bash
# Watch 모드 시작 (기본 경로: ~/.human_typer_input.txt)
python human_typer.py --watch

# 커스텀 경로 지정
python human_typer.py --watch /tmp/type_this.txt

# 타이핑 후 파일 삭제
python human_typer.py --watch --delete

# Watch 모드 + 창 자동 전환 (완전 자동화)
python human_typer.py --watch --delete --window "Notepad"
```

**자동화 사용 예시:**
```bash
# 터미널 1: Watch 모드 실행 (Notepad으로 자동 포커스)
python human_typer.py --watch --delete --window "Notepad"

# 터미널 2 (또는 Claude): 타이핑할 내용 전달
echo "console.log('Hello from Claude!')" > ~/.human_typer_input.txt
```

## Claude/AI 자동화 사용법

Claude나 다른 AI 에이전트가 이 도구를 사용하여 실제 키보드 입력을 시뮬레이션할 수 있습니다.

### 사전 준비

사용자가 미리 Watch 모드를 실행해둬야 합니다:
```bash
# 기본 (수동으로 창 포커스 필요)
python human_typer.py --watch --delete

# 또는 특정 창으로 자동 포커스 (권장)
python human_typer.py --watch --delete --window "Visual Studio Code"
```

### Claude가 타이핑하는 방법

Watch 모드가 실행 중일 때, 아래 파일에 타이핑할 내용을 쓰면 됩니다:

**파일 경로:** `~/.human_typer_input.txt`

**Bash 명령어:**
```bash
cat > ~/.human_typer_input.txt << 'EOF'
여기에 타이핑할 코드나 텍스트를 작성
EOF
```

**예시 - Python 코드 타이핑:**
```bash
cat > ~/.human_typer_input.txt << 'EOF'
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
EOF
```

**예시 - 한 줄 텍스트:**
```bash
echo "console.log('Hello from Claude!');" > ~/.human_typer_input.txt
```

### 동작 흐름

1. Watch 모드가 `~/.human_typer_input.txt` 파일을 감시
2. Claude가 해당 파일에 내용을 작성
3. `--window` 옵션 사용 시 해당 창으로 자동 포커스
4. 3초 카운트다운 후 자동으로 타이핑 시작
5. `--delete` 옵션 사용 시 타이핑 완료 후 파일 자동 삭제

### 완전 자동화 예시

```bash
# 사용자: VS Code에 타이핑하도록 Watch 모드 시작
python human_typer.py --watch --delete --window "Code" -c 1

# Claude: 코드 타이핑 요청
cat > ~/.human_typer_input.txt << 'EOF'
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
EOF
```

### 주의사항

- `--window` 옵션 없이 실행 시 카운트다운 동안 수동으로 창 포커스 필요
- `--window` 옵션 사용 시 자동으로 해당 창으로 포커스 이동
- `--delete` 옵션을 사용하면 반복 사용이 가능합니다
- 창 제목은 부분 매칭 지원 (예: "Code" → "Visual Studio Code")

## 기본 타이핑 속도

빠른 개발자 타이핑 속도(~100 WPM) 기준으로 설정됨:
- Min Delay: 40ms
- Max Delay: 100ms

필요에 따라 더 느리거나 빠르게 조정 가능합니다.

## 프로젝트 구조

```
human-typer/
├── human_typer/
│   ├── __init__.py      # 패키지 초기화
│   ├── __main__.py      # 모듈 진입점
│   ├── cli.py           # CLI 인터페이스
│   ├── config.py        # 설정 상수
│   ├── main_window.py   # 메인 GUI 윈도우
│   └── typing_thread.py # 백그라운드 타이핑 스레드
├── human_typer.py       # 스크립트 진입점
├── run_human_typer.sh   # Linux/macOS 실행 스크립트
├── run_human_typer.bat  # Windows 실행 스크립트
├── requirements.txt     # 의존성 목록
└── README.md
```

## 라이선스

MIT License
