# DevOps 파이프라인 데모 프로젝트

Terraform + GitHub Actions + AWS ECS (Fargate) + Blue/Green 배포를 활용한 완전한 DevOps 파이프라인 데모 프로젝트

## 프로젝트 구조

```
.
├── README.md                           # 메인 README (이 파일)
├── SETUP_GUIDE.md                      # 전체 설정 가이드
├── DEPLOYMENT_GUIDE.md                 # 배포 가이드
├── TROUBLESHOOTING.md                  # 문제 해결 가이드
│
├── backend/                            # Spring Boot 백엔드
│   ├── src/
│   ├── pom.xml
│   ├── Dockerfile
│   ├── README.md
│   └── .dockerignore
│
├── frontend/                           # React 프론트엔드
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── README.md
│   └── .dockerignore
│
├── terraform/                          # Terraform IaC
│   ├── README.md
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── provider.tf
│   ├── terraform.tfvars.example
│   │
│   └── modules/
│       ├── vpc/
│       ├── ecs/
│       ├── alb/
│       ├── ecr/
│       ├── iam/
│       ├── rds/
│       └── codedeploy/
│
├── .github/
│   └── workflows/
│       ├── backend-ci-cd.yml
│       ├── frontend-ci-cd.yml
│       └── pr-check.yml
│
└── docs/                               # 추가 문서
    ├── 01-architecture-overview.md
    ├── 02-terraform-infra-design.md
    ├── 03-github-actions-ci-cd.md
    ├── 04-ecr-ecs-bluegreen.md
    └── 05-application-overview.md
```

---

## 기술 스택

### Backend
- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
- Maven
- MySQL 8.0 (RDS)

### Frontend
- React 18
- Node.js 18
- Nginx (프로덕션)

### Infrastructure
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Container Registry**: Amazon ECR
- **Orchestration**: Amazon ECS (Fargate)
- **Load Balancer**: Application Load Balancer (ALB)
- **Deployment**: AWS CodeDeploy (Blue/Green)
- **Monitoring**: CloudWatch

---

## 빠른 시작 가이드

### 사전 요구사항

1. **AWS 계정**
   - IAM 사용자 생성 (AdministratorAccess 또는 필요한 권한)
   - Access Key ID 및 Secret Access Key

2. **로컬 개발 환경**
   - Java 17
   - Node.js 18+
   - Docker Desktop
   - Terraform 1.0+
   - AWS CLI
   - Git

3. **GitHub 계정**
   - 새 Repository 생성

---

## 단계별 설정 가이드

### 1단계: 로컬에서 애플리케이션 테스트

#### Backend 테스트
```bash
cd backend
mvn clean package
mvn spring-boot:run

# 테스트
curl http://localhost:8080/health
curl http://localhost:8080/api/users
```

#### Frontend 테스트
```bash
cd frontend
npm install
npm start

# 브라우저에서 http://localhost:3000 접속
```

---

### 2단계: Docker 로컬 테스트

#### Backend Docker 빌드 및 실행
```bash
cd backend
docker build -t myapp-backend .
docker run -p 8080:8080 myapp-backend

# 테스트
curl http://localhost:8080/health
```

#### Frontend Docker 빌드 및 실행
```bash
cd frontend
docker build -t myapp-frontend .
docker run -p 80:80 myapp-frontend

# 브라우저에서 http://localhost 접속
```

---

### 3단계: AWS 인프라 구축 (Terraform)

상세한 설정은 [SETUP_GUIDE.md](./SETUP_GUIDE.md)를 참조하세요.

```bash
cd terraform

# 1. AWS 자격 증명 설정
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="ap-northeast-2"

# 2. 변수 파일 생성
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars 파일을 편집하여 프로젝트 이름 등 설정

# 3. Terraform 초기화
terraform init

# 4. 계획 확인
terraform plan

# 5. 인프라 생성 (약 10-15분 소요)
terraform apply

# 6. 출력 값 확인
terraform output
```

**중요**: Terraform이 생성한 출력 값을 기록하세요:
- ECR Repository URLs
- ALB DNS Name
- ECS Cluster Name
- ECS Service Names

---

### 4단계: GitHub Actions 설정

#### 1. GitHub Secrets 등록

Repository → Settings → Secrets and variables → Actions

```
AWS_ACCESS_KEY_ID          # AWS IAM Access Key
AWS_SECRET_ACCESS_KEY      # AWS IAM Secret Key
AWS_REGION                 # ap-northeast-2
```

#### 2. 워크플로우 파일 확인

`.github/workflows/` 디렉토리의 파일들이 자동으로 작동합니다:
- `backend-ci-cd.yml` - 백엔드 배포
- `frontend-ci-cd.yml` - 프론트엔드 배포

#### 3. 코드 Push하여 배포 트리거

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

GitHub Actions가 자동으로 실행되어:
1. 코드 빌드 및 테스트
2. Docker 이미지 생성
3. ECR에 Push
4. ECS에 Blue/Green 배포

---

### 5단계: 배포 확인

#### ALB DNS로 접속

```bash
# Terraform 출력에서 ALB DNS 확인
terraform output alb_dns_name

# 또는 AWS CLI로 확인
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

브라우저에서 접속:
- Frontend: `http://<alb-dns-name>`
- Backend API: `http://<alb-dns-name>/api/users`
- Health Check: `http://<alb-dns-name>/health`

---

## 주요 기능

### 1. 무중단 배포 (Blue/Green with CodeDeploy)
- AWS CodeDeploy를 통한 Blue/Green 배포 지원
- 새 버전 배포 시 기존 서비스 중단 없음
- 자동 Health Check 및 트래픽 전환
- 문제 발생 시 자동 롤백

### 2. 자동화된 CI/CD
- 코드 Push 시 자동 빌드/테스트/배포
- Pull Request 자동 검증
- 환경별 배포 (dev, staging, prod)

### 3. Infrastructure as Code
- Terraform으로 모든 인프라 관리
- 버전 관리 및 재현 가능
- 환경 복제 용이

### 4. 컨테이너 기반 배포
- Docker를 통한 일관된 환경
- Fargate로 서버리스 실행
- 자동 스케일링

---

## 아키텍처 다이어그램

```
┌─────────────┐
│  Developer  │
└──────┬──────┘
       │ git push
       ↓
┌─────────────────────────────────────────┐
│         GitHub Actions (CI/CD)          │
│  ┌──────┐  ┌──────┐  ┌────────┐       │
│  │Build │→ │Test  │→ │Docker  │       │
│  └──────┘  └──────┘  └────┬───┘       │
└────────────────────────────┼───────────┘
                             ↓
                    ┌────────────────┐
                    │   Amazon ECR   │
                    └────────┬───────┘
                             ↓
┌────────────────────────────────────────────┐
│              AWS Infrastructure             │
│  ┌──────────────────────────────────────┐  │
│  │  Application Load Balancer (ALB)     │  │
│  └──────────────┬───────────────────────┘  │
│                 ↓                           │
│  ┌──────────────────────────────────────┐  │
│  │  ECS Service (Blue/Green Deployment) │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐       │  │
│  │  │Task 1│  │Task 2│  │Task 3│       │  │
│  │  └──────┘  └──────┘  └──────┘       │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │     RDS      │  │  CloudWatch  │       │
│  │ (PostgreSQL) │  │   Logs       │       │
│  └──────────────┘  └──────────────┘       │
└────────────────────────────────────────────┘
```

---

## 비용 예상

### 월 예상 비용 (소규모 운영 기준)

| 서비스 | 사양 | 월 예상 비용 |
|--------|------|-------------|
| ECS Fargate | 0.25 vCPU, 0.5GB × 2 Tasks | $15 |
| ALB | 트래픽 10GB | $20 |
| ECR | 스토리지 10GB | $1 |
| RDS (선택) | db.t3.micro | $15 |
| CloudWatch | 로그 5GB | $3 |
| NAT Gateway | 트래픽 10GB | $35 |
| **총계** | | **약 $89/월** |

**비용 절감 팁**:
- 개발 환경은 사용하지 않을 때 중지
- Reserved Instances 활용 (RDS)
- NAT Gateway 대신 VPC Endpoint 사용 고려

---

## 주요 엔드포인트

### Backend API

```bash
# Health Check
GET /health

# 모든 사용자 조회
GET /api/users

# 사용자 상세 조회
GET /api/users/{id}

# 사용자 생성
POST /api/users
Content-Type: application/json
{
  "name": "John Doe",
  "email": "john@example.com"
}

# 사용자 수정
PUT /api/users/{id}

# 사용자 삭제
DELETE /api/users/{id}
```

### Frontend

```bash
# 메인 페이지
GET /

# Health Check
GET /health
```

---

## 모니터링

### CloudWatch Logs

```bash
# Backend 로그 확인
aws logs tail /ecs/myapp-backend --follow

# Frontend 로그 확인
aws logs tail /ecs/myapp-frontend --follow
```

### CloudWatch Metrics

- ECS CPU/Memory 사용률
- ALB Request Count
- Target Response Time
- Healthy/Unhealthy Host Count

---

## 개발 워크플로우

### 1. 새 기능 개발

```bash
# Feature 브랜치 생성
git checkout -b feature/new-feature

# 코드 작성 및 로컬 테스트
mvn test  # Backend
npm test  # Frontend

# 커밋 및 Push
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### 2. Pull Request 생성

- GitHub에서 PR 생성
- 자동으로 PR 검증 워크플로우 실행
- 코드 리뷰 후 main 브랜치로 머지

### 3. 자동 배포

- main 브랜치로 머지 시 자동 배포
- Blue/Green 방식으로 무중단 배포
- CloudWatch에서 배포 모니터링

---

## 환경별 배포

### Development (개발)
```bash
# dev 브랜치에 Push
git push origin dev
```

### Staging (스테이징)
```bash
# staging 브랜치에 Push
git push origin staging
```

### Production (프로덕션)
```bash
# main 브랜치에 머지
git checkout main
git merge staging
git push origin main
```

---

## 롤백 방법

### 1. 자동 롤백
- Health Check 실패 시 자동으로 이전 버전으로 롤백
- CloudWatch Alarm 트리거 시 자동 롤백

### 2. 수동 롤백
```bash
# 이전 Task Definition으로 롤백
aws ecs update-service \
  --cluster myapp-cluster \
  --service myapp-backend-service \
  --task-definition myapp-backend-task:PREVIOUS_VERSION \
  --force-new-deployment
```

---

## 인프라 삭제

**주의**: 모든 리소스가 삭제됩니다!

```bash
cd terraform
terraform destroy
```

---

## 문서

- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - 상세 설정 가이드
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 배포 가이드
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결
- [RDS_SETUP_GUIDE.md](./RDS_SETUP_GUIDE.md) - RDS MySQL 설정 가이드
- [backend/README.md](./backend/README.md) - 백엔드 상세
- [frontend/README.md](./frontend/README.md) - 프론트엔드 상세
- [terraform/README.md](./terraform/README.md) - Terraform 상세

---

## 자주 묻는 질문 (FAQ)

### Q1: 첫 배포 시간은 얼마나 걸리나요?
A: Terraform 인프라 구축 약 10-15분 + 첫 배포 약 5-10분 = 총 15-25분

### Q2: 비용을 절감하려면?
A:
- 개발 환경은 terraform destroy로 삭제 후 필요시 재생성
- Fargate CPU/Memory를 최소화
- NAT Gateway를 1개만 사용 (고가용성 포기)

### Q3: 로컬에서만 테스트하려면?
A: Docker Compose 사용 (별도 docker-compose.yml 제공)

### Q4: HTTPS를 사용하려면?
A: ACM(AWS Certificate Manager)에서 인증서 발급 후 ALB에 적용

### Q5: 데이터베이스는 어떻게 설정하나요?
A: RDS MySQL 모듈이 Terraform에 포함되어 있으며, `terraform apply` 시 자동 생성됩니다. 자세한 내용은 [RDS_SETUP_GUIDE.md](./RDS_SETUP_GUIDE.md)를 참조하세요.

---

## 기여

이 프로젝트는 학습 및 데모 목적으로 작성되었습니다.

---

## 라이선스

MIT License

---

## 문의

프로젝트 관련 문의사항은 Issues에 등록해주세요.

---

## 다음 단계

1. ✅ 로컬에서 애플리케이션 테스트
2. ✅ Docker로 컨테이너화
3. ✅ Terraform으로 AWS 인프라 구축
4. ✅ GitHub Actions로 CI/CD 설정
5. ✅ 첫 배포 실행
6. 📊 CloudWatch 모니터링 설정
7. 🔒 HTTPS 및 보안 강화
8. 📈 Auto Scaling 튜닝
9. ✅ RDS MySQL 데이터베이스 연동
10. 🚀 프로덕션 배포

**프로젝트 시작하기**: [SETUP_GUIDE.md](./SETUP_GUIDE.md)를 참조하세요!
