# TwinKeep — CLAUDE.md

개인 공간의 디지털 트윈 플랫폼.  
대기업(NVIDIA, Google)이 구축하는 세계 트윈의 **경계면(boundary)** 에서,
개인이 자신의 공간·기기·데이터를 완전히 소유·통제하며 외부 트윈과 선택적으로 연결한다.

**GitHub**: https://github.com/wonjinsoft/twinkeep

---

## 아키텍처 (2-레이어, 절대 변경 금지)

```
Omniverse (NVIDIA, RTX 5060 Laptop)
  └── 3D 씬 렌더링 / USD 씬 관리
  └── Kit Extension (Python) ← TwinKeep API 폴링 → USD Prim 속성 갱신
        ↑ USD 파일 교환
TwinKeep (우리가 만드는 것)
  └── FastAPI + Redis + PostgreSQL
  └── 기기 등록, 실시간 상태, 보안/소유권, 접근 제어
  └── MQTT or WebSocket (기기 ↔ 서버)
        ↑ 센서 데이터
기기들 (폰 / PC / IoT / 칩 달린 사물)
```

**핵심 원칙: 3D는 Omniverse가 담당. TwinKeep은 데이터·보안·소유권 레이어.**  
**R3F / Three.js로 3D를 직접 구현하지 않는다.**

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 백엔드 | Python 3.11 · FastAPI · Redis · PostgreSQL |
| 기기 통신 | MQTT (Paho) or WebSocket |
| 3D 씬 | NVIDIA Omniverse · USD Composer · Kit Extension (Python) |
| 웹 대시보드 | React · TypeScript · Vite · Tailwind CSS · Zustand (2D 상태 패널만) |
| 모바일 에이전트 | .NET MAUI (C#) |
| 인프라 | Railway (백엔드) · Vercel (프론트) · Cloudflare (DNS) |
| GPU | NVIDIA GeForce RTX 5060 Laptop |

---

## 도메인 모델

### Entity (모든 트윈의 기본 단위)
```
Entity
├── id: string (UUID, 난독화)
├── type: enum (space, device, agent)
├── name: string
├── metadata: JSON (로컬 스키마와 분리)
├── state: JSON → Redis에 저장
├── history: Event[] → PostgreSQL에 저장
└── access: AccessRule[] (소유자가 부여)
```

### Space extends Entity
```
Space
├── parent_space_id: string | null
├── children: Space[]
├── devices: Device[]
├── geometry: string | null (USD 파일 참조)
└── location: { lat, lng, alt } | null
```

### Device extends Entity
```
Device
├── current_space_id: string (동적, 이동 가능)
├── device_type: enum (phone, sensor, equipment, appliance, pet, person)
├── capabilities: string[]
└── owner_id: string (Agent ID)
```

### Agent extends Entity
```
Agent
├── agent_type: enum (person, service, external_system)
├── owned_spaces: string[]
├── owned_devices: string[]
└── permissions: Permission[]
```

---

## 보안 모델: 스키마-데이터 분리 (Level 1)

**서버에는 숫자만 저장. 의미(스키마)는 사용자 기기에만.**

```
서버 저장: {"eid":"a7x9f2","ts":1712678400,"v":[0.49,0.65,0.34]}
로컬 스키마: temperature(min=-10,max=50), humidity(0~100), lux(0~1000)
복원: 0.49 → 24.5°C
```

---

## Redis Key 구조

```
twin:space:{space_id}:state
twin:device:{device_id}:state
twin:agent:{agent_id}:state
twin:space:{space_id}:meta
twin:device:{device_id}:meta
```

---

## API 구조

```
POST   /entities                    # 생성
GET    /entities/{id}               # 조회
GET    /entities/{id}/state         # 현재 상태
PUT    /entities/{id}/state         # 상태 갱신
GET    /entities/{id}/history       # 이력 조회
PUT    /entities/{id}/access        # 접근 규칙

GET    /spaces/{id}/children        # 하위 공간
GET    /spaces/{id}/devices         # 소속 기기
GET    /spaces/{id}/tree            # 계층 트리

PUT    /devices/{id}/location       # 기기 위치 갱신 (공간 이동)

GET    /agents/{id}/spaces          # 소유 공간
GET    /agents/{id}/devices         # 소유 기기
```

---

## 폴더 구조

```
twinkeep/
├── api/                  # FastAPI 백엔드
│   ├── domain/           # Entity, Space, Device, Agent 모델
│   ├── routers/          # API 라우터
│   ├── services/         # Redis, PostgreSQL 서비스
│   └── omniverse/        # Omniverse 브릿지 (Phase 2)
├── agents/               # 기기 에이전트
│   ├── phone/            # 폰 MQTT 에이전트 (MAUI)
│   └── mock/             # 시뮬레이터
├── omniverse/            # Kit Extension
│   └── twinkeep_ext/     # Omniverse ↔ TwinKeep 브릿지
├── web/                  # 2D 관리 대시보드 (React, 3D 없음)
├── schemas/              # 로컬 스키마 정의 (보안 Level 1)
├── docs/
│   └── architecture.md
└── CLAUDE.md
```

---

## 개발 Phase

### Phase 1 — 데이터 레이어 ✅ 완료
목표: Omniverse 없이도 동작하는 기기 등록·상태·소유권 API

- [x] FastAPI 프로젝트 뼈대 + Docker Compose (Podman)
- [x] Entity/Space/Device/Agent PostgreSQL 스키마
- [x] Redis 상태 레이어 (보안 Level 1: 정규화된 값 배열)
- [x] WebSocket 실시간 상태 스트림 (/ws/devices)
- [x] 기기 등록 API
- [ ] 폰 에이전트 → API 연결 (MAUI 재활용) ← Phase 3로 이동
- [ ] JWT 인증 ← Phase 3로 이동

### Phase 2 — Omniverse 연결
- [ ] USD Composer로 집 씬 생성
- [ ] Kit Extension: TwinKeep API → USD Prim 속성 갱신
- [ ] 실시간 센서 → Omniverse 씬 반영

### Phase 3 — 소유권·접근 제어
- [ ] Space 소유자 모델
- [ ] 접근 규칙 (누구에게 어떤 필드를 공개할지)
- [ ] 경계면 프로토콜

### Phase 4 — 도면 → 3D
- [ ] 도면 이미지 → USD 자동 생성
- [ ] 텍스트 프롬프트 → 파라메트릭 USD 생성

---

## 오늘의 시작점

**2026-04-18**: Phase 1 완료.
- GitHub `wonjinsoft/twinkeep` 재생성, 새 아키텍처로 초기화
- FastAPI + PostgreSQL + Redis + WebSocket 구현 완료
- Podman으로 로컬 실행 중 (`podman-compose up -d`)
- 테스트 파일: `test_ws.py` (WebSocket 수신), `test_state.py` (상태 갱신)
- 다음 작업: Phase 2 — Omniverse Kit SDK 설치 + Kit Extension 개발

---

## 컨텍스트 유지 규칙

1. 세션 종료 전 반드시 "오늘의 시작점" 섹션 업데이트
2. 구조적 결정 전 반드시 `/advisor` 호출
3. Phase 체크리스트를 완료 시마다 즉시 체크

---

## 허용 명령 (Claude 자동 승인)

```
git status / git log / git diff
git add / git commit / git push
python / pip / uvicorn
npm / npx / node
docker / docker-compose / podman / podman-compose
mkdir / ls / cat / cp / mv
```
