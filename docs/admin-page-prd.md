# SI-EcoPass 관리자 페이지 PRD

## 📋 문서 정보

- **프로젝트**: SI-EcoPass Admin Page
- **작성일**: 2025-12-29
- **대상**: 관리자 웹 프론트엔드 개발 에이전트
- **기술 스택**: Next.js 14+, shadcn/ui, Tailwind CSS, Kakao Map API

---

## 🎯 프로젝트 개요

### 목적
대구 지하철 환승 주차장 이용 장려 플랫폼(SI-EcoPass)의 관리자가 사용자 여정을 검토하고 승인/반려할 수 있는 웹 기반 관리자 인터페이스 구축.

### 핵심 기능
1. **여정 승인/반려**: 사용자가 제출한 여정(출발→환승→도착)을 검토하여 포인트 지급 여부 결정
2. **지도 기반 검토**: Kakao Map으로 실제 동선을 시각화하여 진위 여부 판단
3. **통계 대시보드**: 승인 대기 건수, 일일/주간/월간 통계 모니터링

### 사용자
- 대구시 또는 EcoPass 운영팀 관리자
- 일일 승인 예상 건수: 10-50건 (소규모)

---

## 🛠️ 기술 스택

| 항목 | 기술 | 버전 | 비고 |
|------|------|------|------|
| **Framework** | Next.js (App Router) | 14+ | React Server Components 활용 |
| **UI Library** | shadcn/ui | latest | Radix UI + Tailwind 기반, 테마 시스템 내장 |
| **스타일링** | Tailwind CSS | 3.4+ | CSS 변수 기반 테마 |
| **아이콘** | lucide-react | latest | Tree-shakeable, 일관된 디자인 |
| **지도** | Kakao Map JavaScript API | v3 | 대구 지역 최적화 |
| **상태 관리** | TanStack Query (React Query) | v5 | 서버 상태 관리 |
| **폼 관리** | React Hook Form | v7 | 승인/반려 폼 (선택) |
| **인증** | JWT (Supabase Auth) | - | 백엔드 API 인증 |

---

## 🎨 테마 시스템 설계

> **중요**: 이 프로젝트는 shadcn/ui의 테마 시스템을 적극 활용합니다. CSS 변수 기반으로 일관된 디자인과 다크모드를 지원합니다.

### CSS 변수 기반 색상 팔레트

**`app/globals.css`에 정의할 CSS 변수:**

```css
@layer base {
  :root {
    /* Background & Foreground */
    --background: 0 0% 100%;           /* White */
    --foreground: 222.2 84% 4.9%;      /* 거의 검정 */

    /* Card */
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    /* Popover */
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;

    /* Primary (Blue) */
    --primary: 221.2 83.2% 53.3%;      /* #3B82F6 (Blue-500) */
    --primary-foreground: 210 40% 98%;

    /* Secondary (Neutral) */
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    /* Muted */
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    /* Accent (Indigo) */
    --accent: 217.2 91.2% 59.8%;       /* #6366F1 (Indigo-500) */
    --accent-foreground: 210 40% 98%;

    /* Destructive (Red) */
    --destructive: 0 84.2% 60.2%;      /* #EF4444 (Red-500) */
    --destructive-foreground: 210 40% 98%;

    /* Success (Green) - Custom */
    --success: 142.1 76.2% 36.3%;      /* #10B981 (Emerald-500) */
    --success-foreground: 0 0% 100%;

    /* Warning (Yellow) - Custom */
    --warning: 38.7 92.1% 50.2%;       /* #F59E0B (Amber-500) */
    --warning-foreground: 0 0% 100%;

    /* Border */
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;

    /* Ring (Focus) */
    --ring: 221.2 83.2% 53.3%;         /* Primary와 동일 */

    /* Radius */
    --radius: 0.5rem;                  /* 8px */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;

    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;

    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;

    --primary: 217.2 91.2% 59.8%;      /* 다크모드에서 더 밝은 Blue */
    --primary-foreground: 222.2 47.4% 11.2%;

    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;

    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;

    --accent: 217.2 91.2% 59.8%;
    --accent-foreground: 210 40% 98%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;

    --success: 142.1 70.6% 45.3%;
    --success-foreground: 0 0% 100%;

    --warning: 38.7 92.1% 50.2%;
    --warning-foreground: 0 0% 100%;

    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;

    --ring: 224.3 76.3% 48%;
  }
}
```

### Tailwind Config 확장

**`tailwind.config.ts`:**

```typescript
export default {
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          foreground: "hsl(var(--warning-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
}
```

### 다크모드 지원

**Provider 설정:**
```tsx
// app/providers.tsx
import { ThemeProvider } from "next-themes"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
      {children}
    </ThemeProvider>
  )
}
```

**테마 토글 버튼:**
- Header에 Sun/Moon 아이콘 (lucide-react)
- 클릭 시 라이트/다크 토글

---

## 🎭 lucide-react 아이콘 시스템

### 사용할 주요 아이콘

| 용도 | 아이콘 | import |
|------|--------|--------|
| **통계 카드** | | |
| 승인 대기 | `Clock`, `AlertCircle` | `lucide-react` |
| 승인 완료 | `CheckCircle2`, `Check` | `lucide-react` |
| 총 여정 | `Route`, `MapPin` | `lucide-react` |
| 총 사용자 | `Users`, `User` | `lucide-react` |
| **네비게이션** | | |
| 대시보드 | `LayoutDashboard` | `lucide-react` |
| 여정 관리 | `MapPin`, `ListCheck` | `lucide-react` |
| 사용자 관리 | `Users` | `lucide-react` |
| **액션 버튼** | | |
| 승인 | `CheckCircle2`, `ThumbsUp` | `lucide-react` |
| 반려 | `XCircle`, `ThumbsDown` | `lucide-react` |
| 상세 보기 | `Eye`, `ChevronRight` | `lucide-react` |
| **필터/검색** | | |
| 검색 | `Search` | `lucide-react` |
| 필터 | `Filter`, `SlidersHorizontal` | `lucide-react` |
| 날짜 | `Calendar` | `lucide-react` |
| **기타** | | |
| 로그아웃 | `LogOut` | `lucide-react` |
| 테마 토글 | `Sun`, `Moon` | `lucide-react` |
| 로딩 | `Loader2` (animate-spin) | `lucide-react` |
| 에러 | `AlertTriangle` | `lucide-react` |
| 닫기 | `X` | `lucide-react` |
| 이미지 확대 | `ZoomIn`, `Maximize2` | `lucide-react` |
| 주차장 | `ParkingCircle` | `lucide-react` |
| 지하철 | `Train` | `lucide-react` |

### 아이콘 사용 원칙

1. **크기 일관성**:
   - 카드 아이콘: `size={24}` (1.5rem)
   - 버튼 아이콘: `size={16}` (1rem)
   - 테이블 아이콘: `size={18}` (1.125rem)

2. **색상**:
   - 테마 변수 사용: `className="text-muted-foreground"`
   - 상태별 색상: `text-success`, `text-destructive`, `text-warning`

3. **Stroke Width**:
   - 기본: `strokeWidth={2}`
   - 강조: `strokeWidth={2.5}`

---

## 📱 페이지 구조

```
/admin
├── / (대시보드)
├── /trips (여정 관리)
│   └── /trips/[id] (여정 상세 - 모달 또는 별도 페이지)
└── /login (로그인 - 선택)
```

---

## 🖼️ 상세 화면 기획

### 레이아웃 시스템

**컨테이너 구조:**
```
<body class="bg-background text-foreground">
  <div class="flex h-screen">
    <!-- Sidebar (선택) -->
    <aside class="w-64 bg-card border-r border-border">
      ...
    </aside>

    <!-- Main -->
    <main class="flex-1 overflow-auto">
      <!-- Header -->
      <header class="sticky top-0 z-50 bg-background/95 backdrop-blur border-b border-border">
        ...
      </header>

      <!-- Content -->
      <div class="container mx-auto p-6 max-w-7xl">
        ...
      </div>
    </main>
  </div>
</body>
```

**Grid 시스템:**
- 최대 너비: `max-w-7xl` (1280px)
- 컨테이너 패딩: `p-6` (24px)
- Grid: Tailwind의 `grid-cols-{n}` 활용

---

### 1. 대시보드 페이지 (`/admin`)

#### 상세 와이어프레임

```
┌───────────────────────────────────────────────────────────────────────┐
│  Header (h-16, sticky, bg-background/95, border-b)                    │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  SI-EcoPass 관리자 (text-xl font-bold)      [Sun] [Profile] [▼]│ │
│  └─────────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Main Content (p-6, max-w-7xl, mx-auto)                               │
│                                                                        │
│  📊 주요 통계 (mb-8)                                                  │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ <h2 class="text-2xl font-bold mb-4">대시보드</h2>             │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                        │
│  통계 카드 Grid (grid grid-cols-4 gap-4)                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ Card 1  │  │ Card 2  │  │ Card 3  │  │ Card 4  │                │
│  │ (p-6)   │  │ (p-6)   │  │ (p-6)   │  │ (p-6)   │                │
│  │         │  │         │  │         │  │         │                │
│  │ [Clock] │  │ [Check] │  │ [Route] │  │ [Users] │                │
│  │ 승인대기│  │ 오늘승인│  │ 총여정  │  │ 총사용자│                │
│  │  12건   │  │  5건    │  │ 1,234건 │  │ 156명   │                │
│  │         │  │ 반려 2건│  │         │  │         │                │
│  │ (text-  │  │ (text-  │  │ (text-  │  │ (text-  │                │
│  │ warning)│  │ success)│  │ muted)  │  │ muted)  │                │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                │
│  ↑ w-full, h-auto, rounded-lg, border, shadow-sm                     │
│  ↑ hover:shadow-md transition-shadow                                  │
│                                                                        │
│  🔔 최근 승인 대기 여정 (mt-8)                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ <div class="flex justify-between items-center mb-4">         │    │
│  │   <h3 class="text-lg font-semibold">최근 승인 대기 여정</h3>  │    │
│  │   <Button variant="outline" size="sm">전체 보기 →</Button>   │    │
│  │ </div>                                                        │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                        │
│  <Table> (rounded-md border)                                          │
│  ┌─────┬────────┬─────────┬────────────┬────────┬────────┬──────┐   │
│  │ 사용│ 차량번 │ 경로     │ 예상포인트 │ 완료시 │ 상태   │ 액션 │   │
│  │ 자  │ 호     │         │           │ 간     │        │      │   │
│  ├─────┼────────┼─────────┼────────────┼────────┼────────┼──────┤   │
│  │홍길동│12가3456│반월당→  │ 150pt     │1시간전 │[Badge] │[Eye] │   │
│  │     │        │중앙로   │           │        │대기중  │      │   │
│  ├─────┼────────┼─────────┼────────────┼────────┼────────┼──────┤   │
│  │김철수│34나5678│대공원→  │ 200pt     │2시간전 │[Badge] │[Eye] │   │
│  │     │        │동대구   │           │        │대기중  │      │   │
│  └─────┴────────┴─────────┴────────────┴────────┴────────┴──────┘   │
│  ↑ hover:bg-muted/50 (행 호버)                                       │
│  ↑ cursor-pointer (행 클릭 가능)                                     │
│                                                                        │
└───────────────────────────────────────────────────────────────────────┘
```

#### 컴포넌트 상세 스펙

**1) 통계 카드 (Card)**

```tsx
<Card className="overflow-hidden transition-shadow hover:shadow-md">
  <CardHeader className="flex flex-row items-center justify-between pb-2">
    <CardTitle className="text-sm font-medium text-muted-foreground">
      승인 대기
    </CardTitle>
    <Clock className="h-4 w-4 text-warning" />
  </CardHeader>
  <CardContent>
    <div className="text-2xl font-bold">12건</div>
    {/* 부가 정보 (선택) */}
    <p className="text-xs text-muted-foreground mt-1">
      어제보다 +3건
    </p>
  </CardContent>
</Card>
```

**색상 매핑 (테마 변수 사용):**
- 승인 대기: `text-warning` (Yellow)
- 승인 완료: `text-success` (Green)
- 총 여정/사용자: `text-muted-foreground` (Gray)

**2) 테이블 (Table)**

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>사용자</TableHead>
      <TableHead>차량번호</TableHead>
      <TableHead>경로</TableHead>
      <TableHead>예상 포인트</TableHead>
      <TableHead>완료 시간</TableHead>
      <TableHead>상태</TableHead>
      <TableHead className="text-right">액션</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {trips.map((trip) => (
      <TableRow
        key={trip.id}
        className="cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={() => openTripDetail(trip.id)}
      >
        <TableCell className="font-medium">{trip.user.username}</TableCell>
        <TableCell className="text-muted-foreground">{trip.user.vehicle_number}</TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <ParkingCircle className="h-4 w-4 text-muted-foreground" />
            <span>{trip.route_summary}</span>
          </div>
        </TableCell>
        <TableCell className="font-semibold">{trip.estimated_points}pt</TableCell>
        <TableCell className="text-muted-foreground text-sm">
          {formatRelativeTime(trip.completed_at)}
        </TableCell>
        <TableCell>
          <Badge variant="warning" className="gap-1">
            <Clock className="h-3 w-3" />
            승인 대기
          </Badge>
        </TableCell>
        <TableCell className="text-right">
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <Eye className="h-4 w-4" />
          </Button>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

**Badge variant 커스텀 (필요 시):**
```tsx
// components/ui/badge.tsx에 추가
{
  warning: "bg-warning/10 text-warning border-warning/20 hover:bg-warning/20",
  success: "bg-success/10 text-success border-success/20 hover:bg-success/20",
}
```

---

### 2. 여정 관리 페이지 (`/admin/trips`)

#### 상세 와이어프레임

```
┌───────────────────────────────────────────────────────────────────────┐
│  Header (동일)                                                         │
├───────────────────────────────────────────────────────────────────────┤
│  Main Content (p-6, max-w-7xl)                                         │
│                                                                        │
│  <h1 class="text-3xl font-bold mb-6">여정 관리</h1>                   │
│                                                                        │
│  필터 바 (bg-card, rounded-lg, border, p-4, mb-6)                     │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ <div class="flex gap-4 items-center">                        │    │
│  │                                                               │    │
│  │  [Select: 상태]  [Popover: 날짜]  [Input: 검색]  [Button]   │    │
│  │   ↓ w-48         ↓ w-64          ↓ w-80        ↓ "검색"     │    │
│  │                                                               │    │
│  │  <Filter/>       <Calendar/>     <Search/>                   │    │
│  │  아이콘           아이콘           아이콘                     │    │
│  │                                                               │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                        │
│  테이블 (Table)                                                       │
│  ┌─────┬─────┬────────┬─────────┬──────┬──────┬────────┬──────┐     │
│  │ ID  │사용 │차량번호│ 경로     │포인트│ 상태 │완료시간│ 액션 │     │
│  │     │자   │        │         │      │      │        │      │     │
│  ├─────┼─────┼────────┼─────────┼──────┼──────┼────────┼──────┤     │
│  │#123 │홍길 │12가3456│반월당→  │150pt │[Badge│2시간전 │[Eye] │     │
│  │     │동   │        │중앙로   │      │대기중│        │      │     │
│  ├─────┼─────┼────────┼─────────┼──────┼──────┼────────┼──────┤     │
│  │...  │     │        │         │      │]     │        │      │     │
│  └─────┴─────┴────────┴─────────┴──────┴──────┴────────┴──────┘     │
│                                                                        │
│  페이지네이션 (mt-4)                                                  │
│  <div class="flex justify-between items-center">                      │
│    <p class="text-sm text-muted-foreground">총 156건 중 1-20건</p>   │
│    <Pagination>                                                       │
│      [◀ 이전] [1] [2] [3] ... [8] [다음 ▶]                          │
│    </Pagination>                                                      │
│  </div>                                                               │
│                                                                        │
└───────────────────────────────────────────────────────────────────────┘
```

#### 컴포넌트 상세 스펙

**1) 필터 바**

```tsx
<Card>
  <CardContent className="p-4">
    <div className="flex gap-4 items-center flex-wrap">
      {/* 상태 필터 */}
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="상태 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체</SelectItem>
            <SelectItem value="COMPLETED">승인 대기</SelectItem>
            <SelectItem value="APPROVED">승인 완료</SelectItem>
            <SelectItem value="REJECTED">반려</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 날짜 필터 */}
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-64 justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <Calendar className="mr-2 h-4 w-4" />
            {date ? format(date, "PPP", { locale: ko }) : "날짜 선택"}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="range"
            selected={date}
            onSelect={setDate}
            initialFocus
          />
        </PopoverContent>
      </Popover>

      {/* 검색 */}
      <div className="flex-1 min-w-[320px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="사용자명 또는 차량번호로 검색"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* 검색 버튼 */}
      <Button onClick={handleSearch}>
        검색
      </Button>
    </div>
  </CardContent>
</Card>
```

**2) 테이블 (동일하지만 더 많은 컬럼)**

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead className="w-24">ID</TableHead>
      <TableHead>사용자</TableHead>
      <TableHead>차량번호</TableHead>
      <TableHead>경로</TableHead>
      <TableHead className="text-right">예상 포인트</TableHead>
      <TableHead>상태</TableHead>
      <TableHead>완료 시간</TableHead>
      <TableHead className="text-right">액션</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {/* 로딩 상태 */}
    {isLoading && (
      <TableRow>
        <TableCell colSpan={8} className="h-24 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto text-muted-foreground" />
          <p className="text-sm text-muted-foreground mt-2">로딩 중...</p>
        </TableCell>
      </TableRow>
    )}

    {/* 빈 상태 */}
    {!isLoading && trips.length === 0 && (
      <TableRow>
        <TableCell colSpan={8} className="h-24 text-center">
          <AlertTriangle className="h-6 w-6 mx-auto text-muted-foreground" />
          <p className="text-sm text-muted-foreground mt-2">
            조회된 여정이 없습니다.
          </p>
        </TableCell>
      </TableRow>
    )}

    {/* 데이터 */}
    {trips.map((trip) => (
      <TableRow key={trip.id} className="cursor-pointer hover:bg-muted/50">
        <TableCell className="font-mono text-xs text-muted-foreground">
          #{trip.id.slice(0, 8)}
        </TableCell>
        <TableCell className="font-medium">{trip.user.username}</TableCell>
        <TableCell className="text-muted-foreground">
          {trip.user.vehicle_number}
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2 text-sm">
            <ParkingCircle className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="truncate max-w-xs">{trip.route_summary}</span>
          </div>
        </TableCell>
        <TableCell className="text-right font-semibold">
          {trip.estimated_points}pt
        </TableCell>
        <TableCell>
          <Badge
            variant={
              trip.status === "APPROVED"
                ? "success"
                : trip.status === "REJECTED"
                ? "destructive"
                : "warning"
            }
          >
            {getStatusLabel(trip.status)}
          </Badge>
        </TableCell>
        <TableCell className="text-sm text-muted-foreground">
          {formatRelativeTime(trip.completed_at)}
        </TableCell>
        <TableCell className="text-right">
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={(e) => {
              e.stopPropagation()
              openTripDetail(trip.id)
            }}
          >
            <Eye className="h-4 w-4" />
            <span className="sr-only">상세 보기</span>
          </Button>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

---

### 3. 여정 상세 모달 (`Dialog`)

#### 상세 와이어프레임

```
┌───────────────────────────────────────────────────────────────────────┐
│  Dialog Overlay (bg-black/50)                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ DialogContent (max-w-4xl, max-h-[90vh], overflow-auto)         │  │
│  │ ┌───────────────────────────────────────────────────────────┐  │  │
│  │ │ DialogHeader (border-b, pb-4)                             │  │  │
│  │ │ <div class="flex justify-between items-start">            │  │  │
│  │ │   <div>                                                    │  │  │
│  │ │     <DialogTitle class="text-2xl font-bold">             │  │  │
│  │ │       여정 상세 정보                                       │  │  │
│  │ │     </DialogTitle>                                        │  │  │
│  │ │     <DialogDescription class="text-muted-foreground">    │  │  │
│  │ │       #550e8400 | 2025-01-01 10:00                        │  │  │
│  │ │     </DialogDescription>                                  │  │  │
│  │ │   </div>                                                   │  │  │
│  │ │   <DialogClose>                                           │  │  │
│  │ │     <Button variant="ghost" size="sm"><X /></Button>     │  │  │
│  │ │   </DialogClose>                                          │  │  │
│  │ │ </div>                                                     │  │  │
│  │ └───────────────────────────────────────────────────────────┘  │  │
│  │                                                                 │  │
│  │ <div class="space-y-6 p-6">                                    │  │
│  │                                                                 │  │
│  │   👤 사용자 정보 섹션 (Card)                                   │  │
│  │   ┌─────────────────────────────────────────────────────────┐ │  │
│  │   │ <CardHeader>                                            │ │  │
│  │   │   <CardTitle class="flex items-center gap-2">          │ │  │
│  │   │     <User class="h-5 w-5" />                           │ │  │
│  │   │     사용자 정보                                        │ │  │
│  │   │   </CardTitle>                                         │ │  │
│  │   │ </CardHeader>                                          │ │  │
│  │   │ <CardContent>                                          │ │  │
│  │   │   <dl class="grid grid-cols-2 gap-4">                 │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt class="text-sm text-muted-foreground">이름</dt>│ │  │
│  │   │       <dd class="font-medium">홍길동</dd>              │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt class="text-sm text-muted-foreground">      │ │  │
│  │   │         차량번호                                       │ │  │
│  │   │       </dt>                                            │ │  │
│  │   │       <dd class="font-medium font-mono">12가3456</dd> │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt>이메일</dt>                                  │ │  │
│  │   │       <dd>hong@example.com</dd>                        │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt>보유 포인트</dt>                             │ │  │
│  │   │       <dd class="text-lg font-bold text-primary">     │ │  │
│  │   │         1,500pt                                        │ │  │
│  │   │       </dd>                                            │ │  │
│  │   │     </div>                                             │ │  │
│  │   │   </dl>                                                │ │  │
│  │   │ </CardContent>                                         │ │  │
│  │   └─────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │   🗺️ 지도 섹션 (Card)                                         │  │
│  │   ┌─────────────────────────────────────────────────────────┐ │  │
│  │   │ <CardHeader>                                            │ │  │
│  │   │   <CardTitle class="flex items-center gap-2">          │ │  │
│  │   │     <MapPin class="h-5 w-5" />                         │ │  │
│  │   │     여정 경로                                          │ │  │
│  │   │   </CardTitle>                                         │ │  │
│  │   │ </CardHeader>                                          │ │  │
│  │   │ <CardContent>                                          │ │  │
│  │   │   <div id="map" class="w-full h-96 rounded-md border">│ │  │
│  │   │     [Kakao Map]                                        │ │  │
│  │   │     🅿️ ────→ 🚇 ────→ 🚇                             │ │  │
│  │   │     출발    환승    도착                               │ │  │
│  │   │   </div>                                               │ │  │
│  │   │   {/* 마커 범례 */}                                    │ │  │
│  │   │   <div class="flex gap-4 mt-4 text-sm">               │ │  │
│  │   │     <div class="flex items-center gap-2">             │ │  │
│  │   │       <ParkingCircle class="h-4 w-4 text-destructive"/>│ │  │
│  │   │       <span>출발 (주차장)</span>                       │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <div class="flex items-center gap-2">             │ │  │
│  │   │       <Train class="h-4 w-4 text-primary" />          │ │  │
│  │   │       <span>환승 (역)</span>                           │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <div class="flex items-center gap-2">             │ │  │
│  │   │       <Train class="h-4 w-4 text-success" />          │ │  │
│  │   │       <span>도착 (역)</span>                           │ │  │
│  │   │     </div>                                             │ │  │
│  │   │   </div>                                               │ │  │
│  │   │ </CardContent>                                         │ │  │
│  │   └─────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │   📸 인증 사진 섹션 (Card)                                     │  │
│  │   ┌─────────────────────────────────────────────────────────┐ │  │
│  │   │ <CardHeader>                                            │ │  │
│  │   │   <CardTitle class="flex items-center gap-2">          │ │  │
│  │   │     <Image class="h-5 w-5" />                          │ │  │
│  │   │     인증 사진                                          │ │  │
│  │   │   </CardTitle>                                         │ │  │
│  │   │ </CardHeader>                                          │ │  │
│  │   │ <CardContent>                                          │ │  │
│  │   │   <div class="grid grid-cols-2 gap-4">                │ │  │
│  │   │     {/* 환승 사진 */}                                  │ │  │
│  │   │     <div class="space-y-2">                            │ │  │
│  │   │       <p class="text-sm font-medium">환승 인증</p>     │ │  │
│  │   │       <button                                          │ │  │
│  │   │         class="relative aspect-square rounded-md        │ │  │
│  │   │                overflow-hidden border-2 hover:border-   │ │  │
│  │   │                primary transition-colors cursor-pointer"│ │  │
│  │   │       >                                                 │ │  │
│  │   │         <img src={signedUrl} class="object-cover" />   │ │  │
│  │   │         <div class="absolute inset-0 bg-black/40       │ │  │
│  │   │                     opacity-0 hover:opacity-100         │ │  │
│  │   │                     transition-opacity flex items-      │ │  │
│  │   │                     center justify-center">            │ │  │
│  │   │           <ZoomIn class="h-8 w-8 text-white" />        │ │  │
│  │   │         </div>                                          │ │  │
│  │   │       </button>                                         │ │  │
│  │   │     </div>                                              │ │  │
│  │   │                                                          │ │  │
│  │   │     {/* 도착 사진 */}                                  │ │  │
│  │   │     <div class="space-y-2">                            │ │  │
│  │   │       <p class="text-sm font-medium">도착 인증</p>     │ │  │
│  │   │       <button class="...">                             │ │  │
│  │   │         [동일 구조]                                     │ │  │
│  │   │       </button>                                         │ │  │
│  │   │     </div>                                              │ │  │
│  │   │   </div>                                                │ │  │
│  │   │ </CardContent>                                         │ │  │
│  │   └─────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │   ℹ️ 여정 정보 섹션 (Card)                                     │  │
│  │   ┌─────────────────────────────────────────────────────────┐ │  │
│  │   │ <CardHeader>                                            │ │  │
│  │   │   <CardTitle>여정 정보</CardTitle>                      │ │  │
│  │   │ </CardHeader>                                          │ │  │
│  │   │ <CardContent>                                          │ │  │
│  │   │   <div class="grid grid-cols-3 gap-4">                │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt>시작</dt>                                    │ │  │
│  │   │       <dd class="flex items-center gap-2 mt-1">       │ │  │
│  │   │         <Clock class="h-4 w-4 text-muted-foreground" />│ │  │
│  │   │         09:00                                          │ │  │
│  │   │       </dd>                                            │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt>환승</dt>                                    │ │  │
│  │   │       <dd class="flex items-center gap-2 mt-1">       │ │  │
│  │   │         <Clock class="h-4 w-4" />                     │ │  │
│  │   │         09:30                                          │ │  │
│  │   │       </dd>                                            │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt>도착</dt>                                    │ │  │
│  │   │       <dd class="flex items-center gap-2 mt-1">       │ │  │
│  │   │         <Clock class="h-4 w-4" />                     │ │  │
│  │   │         10:00                                          │ │  │
│  │   │       </dd>                                            │ │  │
│  │   │     </div>                                             │ │  │
│  │   │   </div>                                               │ │  │
│  │   │   <Separator class="my-4" />                          │ │  │
│  │   │   <div class="flex justify-between items-center">    │ │  │
│  │   │     <div>                                              │ │  │
│  │   │       <dt class="text-sm text-muted-foreground">      │ │  │
│  │   │         예상 포인트                                    │ │  │
│  │   │       </dt>                                            │ │  │
│  │   │       <dd class="text-2xl font-bold text-primary">    │ │  │
│  │   │         150pt                                          │ │  │
│  │   │       </dd>                                            │ │  │
│  │   │     </div>                                             │ │  │
│  │   │     <Badge variant="warning" class="text-base px-4    │ │  │
│  │   │                                          py-1">        │ │  │
│  │   │       <Clock class="h-4 w-4 mr-1" />                  │ │  │
│  │   │       승인 대기                                        │ │  │
│  │   │     </Badge>                                           │ │  │
│  │   │   </div>                                               │ │  │
│  │   │ </CardContent>                                         │ │  │
│  │   └─────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │   📝 관리자 메모 섹션 (Card)                                   │  │
│  │   ┌─────────────────────────────────────────────────────────┐ │  │
│  │   │ <CardHeader>                                            │ │  │
│  │   │   <CardTitle>관리자 메모</CardTitle>                    │ │  │
│  │   │   <CardDescription>                                    │ │  │
│  │   │     반려 시 사유 입력 필수 (최소 10자)                 │ │  │
│  │   │   </CardDescription>                                   │ │  │
│  │   │ </CardHeader>                                          │ │  │
│  │   │ <CardContent>                                          │ │  │
│  │   │   <Textarea                                            │ │  │
│  │   │     placeholder="승인 또는 반려 사유를 입력하세요..."   │ │  │
│  │   │     value={adminNote}                                  │ │  │
│  │   │     onChange={(e) => setAdminNote(e.target.value)}    │ │  │
│  │   │     className="min-h-[100px] resize-none"             │ │  │
│  │   │     maxLength={500}                                    │ │  │
│  │   │   />                                                    │ │  │
│  │   │   <p class="text-xs text-muted-foreground text-right   │ │  │
│  │   │             mt-2">                                      │ │  │
│  │   │     {adminNote.length} / 500                           │ │  │
│  │   │   </p>                                                  │ │  │
│  │   │ </CardContent>                                         │ │  │
│  │   └─────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │ </div>                                                          │  │
│  │                                                                 │  │
│  │ DialogFooter (border-t, pt-4)                                  │  │
│  │ ┌───────────────────────────────────────────────────────────┐ │  │
│  │ │ <div class="flex justify-end gap-3">                      │ │  │
│  │ │   <Button variant="ghost" onClick={closeDialog}>         │ │  │
│  │ │     취소                                                   │ │  │
│  │ │   </Button>                                               │ │  │
│  │ │   <Button variant="destructive" onClick={handleReject}>  │ │  │
│  │ │     <XCircle class="h-4 w-4 mr-2" />                     │ │  │
│  │ │     반려하기                                               │ │  │
│  │ │   </Button>                                               │ │  │
│  │ │   <Button                                                 │ │  │
│  │ │     className="bg-success hover:bg-success/90"           │ │  │
│  │ │     onClick={handleApprove}                              │ │  │
│  │ │   >                                                        │ │  │
│  │ │     <CheckCircle2 class="h-4 w-4 mr-2" />                │ │  │
│  │ │     승인하기                                               │ │  │
│  │ │   </Button>                                               │ │  │
│  │ │ </div>                                                     │ │  │
│  │ └───────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
```

#### 컴포넌트 상세 스펙

**Dialog 크기 및 스타일:**
```tsx
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
    {/* ... */}
  </DialogContent>
</Dialog>
```

**승인/반려 버튼 색상 (테마 변수 사용):**
```tsx
{/* 승인 버튼 - success 색상 */}
<Button
  className="bg-success text-success-foreground hover:bg-success/90"
  onClick={handleApprove}
>
  <CheckCircle2 className="h-4 w-4 mr-2" />
  승인하기
</Button>

{/* 반려 버튼 - destructive variant */}
<Button variant="destructive" onClick={handleReject}>
  <XCircle className="h-4 w-4 mr-2" />
  반려하기
</Button>
```

---

## 🎨 인터랙션 상태 (Interaction States)

### 버튼 상태

```tsx
// 기본 버튼 (Primary)
<Button>
  클릭하세요
</Button>
// 기본: bg-primary text-primary-foreground
// hover: bg-primary/90
// active: bg-primary/80
// focus: ring-2 ring-ring ring-offset-2
// disabled: opacity-50 cursor-not-allowed

// Outline 버튼
<Button variant="outline">
  클릭하세요
</Button>
// 기본: border-input bg-background
// hover: bg-accent text-accent-foreground
// active: bg-accent/80

// Ghost 버튼
<Button variant="ghost">
  클릭하세요
</Button>
// 기본: transparent
// hover: bg-accent text-accent-foreground
```

### Card 호버

```tsx
<Card className="transition-shadow hover:shadow-md cursor-pointer">
  {/* ... */}
</Card>
```

### Table Row 호버

```tsx
<TableRow className="cursor-pointer hover:bg-muted/50 transition-colors">
  {/* ... */}
</TableRow>
```

### Input Focus

```tsx
<Input />
// focus: border-ring ring-2 ring-ring ring-offset-2
```

---

## 📊 로딩/에러/빈 상태 UI

### 로딩 상태

**1) 전체 페이지 로딩 (Skeleton):**
```tsx
// 통계 카드 로딩
<Card>
  <CardHeader>
    <Skeleton className="h-4 w-24" />
  </CardHeader>
  <CardContent>
    <Skeleton className="h-8 w-16" />
  </CardContent>
</Card>

// 테이블 로딩
<TableBody>
  {Array.from({ length: 5 }).map((_, i) => (
    <TableRow key={i}>
      <TableCell><Skeleton className="h-4 w-20" /></TableCell>
      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
      {/* ... */}
    </TableRow>
  ))}
</TableBody>
```

**2) 부분 로딩 (Spinner):**
```tsx
<Button disabled>
  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
  처리 중...
</Button>
```

### 에러 상태

```tsx
// Alert 컴포넌트
<Alert variant="destructive">
  <AlertTriangle className="h-4 w-4" />
  <AlertTitle>오류 발생</AlertTitle>
  <AlertDescription>
    데이터를 불러오는 중 오류가 발생했습니다.
    <Button variant="link" className="h-auto p-0 ml-1" onClick={retry}>
      다시 시도
    </Button>
  </AlertDescription>
</Alert>
```

### 빈 상태 (Empty State)

```tsx
// 테이블 빈 상태
<TableRow>
  <TableCell colSpan={8} className="h-48 text-center">
    <div className="flex flex-col items-center gap-2">
      <AlertTriangle className="h-12 w-12 text-muted-foreground/50" />
      <h3 className="text-lg font-semibold">조회된 여정이 없습니다</h3>
      <p className="text-sm text-muted-foreground">
        필터 조건을 변경하거나 검색어를 확인해주세요.
      </p>
      <Button variant="outline" onClick={resetFilters} className="mt-4">
        필터 초기화
      </Button>
    </div>
  </TableCell>
</TableRow>
```

---

## 🔄 사용자 플로우

### 승인 플로우 (상세)

```
1. 대시보드 접속
   ↓
2. "최근 승인 대기" 테이블 확인
   - 또는 Sidebar에서 "여정 관리" 클릭
   ↓
3. 여정 목록에서 승인 대기 건 확인
   - 상태 Badge가 "승인 대기" (warning variant)
   - 행 hover 시 bg-muted/50 (시각적 피드백)
   ↓
4. 행 클릭 → Dialog 열림 (애니메이션 with scale)
   ↓
5. 지도에서 동선 확인
   - Kakao Map 로드 (로딩 인디케이터)
   - 3개 마커 자동 표시 (출발-환승-도착)
   - Polyline 연결 (파란색)
   - 마커 클릭 → InfoWindow 표시
   ↓
6. 인증 사진 확인
   - 썸네일 hover → 확대 아이콘 표시 (ZoomIn)
   - 클릭 → Lightbox Dialog 열림
   - Escape 또는 X 버튼으로 닫기
   ↓
7. 사용자 정보 확인
   - 이름, 차량번호, 보유 포인트
   ↓
8. 판단:
   - ✅ 적절함:
     ↓
     "승인하기" 버튼 클릭
     ↓
     AlertDialog 표시: "150pt를 지급하고 승인하시겠습니까?"
     ↓
     "승인" 버튼 클릭
     ↓
     버튼 disabled + Loader2 애니메이션
     ↓
     API 호출: POST /admin/trips/{id}/approve
     ↓
     성공:
       - Toast 표시: "여정이 승인되었습니다 (150pt 지급)"
       - Dialog 닫힘 (애니메이션)
       - 목록 refetch (React Query)
       - 해당 행이 사라지거나 상태 "승인 완료"로 변경
     실패:
       - Toast (variant="destructive"): "승인에 실패했습니다. 다시 시도해주세요."
       - Dialog 열린 상태 유지

   - ❌ 부적절:
     ↓
     Textarea에 반려 사유 입력 (최소 10자 검증)
     ↓
     "반려하기" 버튼 클릭
     ↓
     AlertDialog: "정말 반려하시겠습니까?"
     ↓
     "반려" 버튼 클릭
     ↓
     API 호출: POST /admin/trips/{id}/reject
     ↓
     성공:
       - Toast: "여정이 반려되었습니다"
       - Dialog 닫힘
       - 목록 refetch
       - 상태 "반려"로 변경 (Badge variant="destructive")
     실패:
       - Toast (destructive): 에러 메시지
```

---

## 🔐 인증 및 권한

### Next.js Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value

  if (!token && request.nextUrl.pathname.startsWith('/admin')) {
    return NextResponse.redirect(new URL('/admin/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: '/admin/:path*',
}
```

---

## 📝 개발 참고사항

### shadcn/ui 컴포넌트 설치

```bash
# 초기 설정
npx shadcn-ui@latest init

# 필요한 컴포넌트 설치
npx shadcn-ui@latest add card
npx shadcn-ui@latest add table
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add alert-dialog
npx shadcn-ui@latest add select
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add calendar
npx shadcn-ui@latest add popover
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add pagination
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add alert
```

### 커스텀 Badge Variant 추가

```typescript
// components/ui/badge.tsx
const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "...",
        destructive: "...",
        outline: "...",
        secondary: "...",
        // 커스텀 추가
        success: "bg-success/10 text-success border-success/20 hover:bg-success/20",
        warning: "bg-warning/10 text-warning border-warning/20 hover:bg-warning/20",
      },
    },
  }
)
```

### 환경 변수

```env
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_KAKAO_MAP_APP_KEY=your_kakao_map_key
```

---

## ✅ 체크리스트

### Phase 1 (필수 기능)

**테마 설정**
- [ ] shadcn/ui 초기 설정 (`npx shadcn-ui@latest init`)
- [ ] `globals.css`에 CSS 변수 정의 (light + dark 테마)
- [ ] `tailwind.config.ts` 확장
- [ ] `next-themes` Provider 설정
- [ ] 커스텀 Badge variant (success, warning) 추가

**공통 레이아웃**
- [ ] Header 컴포넌트 (타이틀, 테마 토글, 프로필)
- [ ] Sidebar 컴포넌트 (선택)
- [ ] Container 레이아웃

**대시보드 페이지**
- [ ] 통계 카드 4개 (Card 컴포넌트)
  - [ ] lucide-react 아이콘 적용
  - [ ] 테마 변수 색상 사용
  - [ ] hover 효과
- [ ] 최근 승인 대기 목록 테이블 (Table 컴포넌트)
  - [ ] Badge로 상태 표시
  - [ ] 행 hover 효과
- [ ] API 연동 (GET /admin/dashboard/stats, GET /admin/trips)
- [ ] 로딩 상태 (Skeleton)
- [ ] 에러 상태 (Alert)

**여정 관리 페이지**
- [ ] 필터 바 (Select, Popover + Calendar, Input)
  - [ ] lucide-react 아이콘
  - [ ] 테마 변수 스타일
- [ ] 여정 목록 테이블
  - [ ] Badge variant (success, warning, destructive)
  - [ ] 로딩 상태 (Skeleton, Loader2)
  - [ ] 빈 상태 (AlertTriangle 아이콘)
- [ ] 페이지네이션 (Pagination 컴포넌트)
- [ ] API 연동 (필터 + 페이지네이션)

**여정 상세 모달**
- [ ] Dialog 컴포넌트
- [ ] 사용자 정보 섹션 (Card)
  - [ ] User 아이콘
  - [ ] Grid 레이아웃
- [ ] Kakao Map 지도 뷰
  - [ ] 마커 3개 (ParkingCircle, Train 아이콘 활용)
  - [ ] Polyline
  - [ ] InfoWindow
- [ ] 인증 사진 갤러리
  - [ ] ZoomIn 아이콘 hover 효과
  - [ ] Lightbox Dialog
- [ ] 여정 정보 표시 (Clock 아이콘)
- [ ] 관리자 메모 입력 (Textarea, 글자 수 표시)
- [ ] 승인/반려 버튼
  - [ ] AlertDialog 확인
  - [ ] Loader2 로딩 애니메이션
  - [ ] Toast 알림
- [ ] API 연동 (GET /admin/trips/{id}, POST approve/reject)

### Phase 2 (추후)
- [ ] 다크모드 토글 완전 지원 (모든 컴포넌트)
- [ ] 사용자 관리 페이지
- [ ] 통계/리포트 페이지
- [ ] 로그인 페이지 (shadcn/ui Form 사용)

---

## 🔗 관련 문서 링크

- **shadcn/ui 공식 문서**: https://ui.shadcn.com
- **lucide-react 아이콘**: https://lucide.dev/icons
- **Tailwind CSS**: https://tailwindcss.com
- **next-themes**: https://github.com/pacocoursey/next-themes
- **백엔드 API 문서**: http://localhost:8000/docs (Swagger)
- **Linear Issue**:
  - [URE-162] Backend API 개선
  - [URE-163] Frontend Admin Page 구현
- **Kakao Map API**: https://apis.map.kakao.com/web/

---

**문서 버전**: v2.0 (테마 시스템 적용)
**최종 수정일**: 2025-12-29
