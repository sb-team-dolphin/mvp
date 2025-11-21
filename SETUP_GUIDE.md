# 전체 설정 가이드

이 가이드는 로컬 개발부터 AWS 배포까지 전체 프로세스를 단계별로 설명합니다.

## 목차

1. [로컬 개발 환경 설정](#1-로컬-개발-환경-설정)
2. [로컬에서 애플리케이션 실행](#2-로컬에서-애플리케이션-실행)
3. [Docker 로컬 테스트](#3-docker-로컬-테스트)
4. [AWS 계정 및 IAM 설정](#4-aws-계정-및-iam-설정)
5. [Terraform으로 인프라 구축](#5-terraform으로-인프라-구축)
6. [GitHub 저장소 설정](#6-github-저장소-설정)
7. [GitHub Actions 설정](#7-github-actions-설정)
8. [첫 배포 실행](#8-첫-배포-실행)
9. [배포 확인](#9-배포-확인)

---

## 1. 로컬 개발 환경 설정

### 필수 소프트웨어 설치

#### Windows

```powershell
# Chocolatey로 설치 (관리자 권한)
choco install openjdk17 -y
choco install nodejs -y
choco install maven -y
choco install docker-desktop -y
choco install terraform -y
choco install awscli -y
choco install git -y
```

#### macOS

```bash
# Homebrew로 설치
brew install openjdk@17
brew install node
brew install maven
brew install --cask docker
brew install terraform
brew install awscli
brew install git
```

#### Linux (Ubuntu/Debian)

```bash
# Java 17
sudo apt update
sudo apt install openjdk-17-jdk -y

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Maven
sudo apt install maven -y

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform -y

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 설치 확인

```bash
java -version        # Java 17.x.x
node --version       # v18.x.x 이상
mvn --version        # Maven 3.6.x 이상
docker --version     # Docker 20.x.x 이상
terraform --version  # Terraform 1.0.x 이상
aws --version        # AWS CLI 2.x.x
git --version        # Git 2.x.x
```

---

## 2. 로컬에서 애플리케이션 실행

### 2.1 백엔드 실행

```bash
# 프로젝트 클론 (또는 다운로드)
cd SoftBank/backend

# Maven으로 빌드 및 실행
mvn clean package
mvn spring-boot:run
```

**확인:**
```bash
# Health Check
curl http://localhost:8080/health

# 사용자 API
curl http://localhost:8080/api/users
```

예상 결과:
```json
{
  "status": "UP",
  "service": "myapp-backend",
  "version": "1.0.0"
}
```

### 2.2 프론트엔드 실행

**새 터미널 열기:**

```bash
cd SoftBank/frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

브라우저가 자동으로 http://localhost:3000 열립니다.

**확인:**
- 사용자 목록이 표시되는지 확인
- 사용자 추가/수정/삭제 테스트

---

## 3. Docker 로컬 테스트

### 3.1 백엔드 Docker 테스트

```bash
cd backend

# Docker 이미지 빌드
docker build -t myapp-backend:local .

# 컨테이너 실행
docker run -d --name backend -p 8080:8080 myapp-backend:local

# 로그 확인
docker logs -f backend

# 테스트
curl http://localhost:8080/health

# 컨테이너 중지 및 삭제
docker stop backend
docker rm backend
```

### 3.2 프론트엔드 Docker 테스트

```bash
cd frontend

# Docker 이미지 빌드
docker build -t myapp-frontend:local .

# 컨테이너 실행
docker run -d --name frontend -p 80:80 myapp-frontend:local

# 브라우저에서 http://localhost 접속

# 컨테이너 중지 및 삭제
docker stop frontend
docker rm frontend
```

### 3.3 Docker Compose로 전체 스택 실행 (선택)

`docker-compose.yml` 파일 생성:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=dev

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8080
```

실행:
```bash
docker-compose up --build
```

---

## 4. AWS 계정 및 IAM 설정

### 4.1 AWS 계정 생성

1. https://aws.amazon.com 접속
2. "Create an AWS Account" 클릭
3. 이메일, 비밀번호, 결제 정보 입력

### 4.2 IAM 사용자 생성

1. AWS Console → IAM → Users → Add users
2. 사용자 이름: `terraform-user`
3. Access type: Programmatic access ✅
4. Permissions: `AdministratorAccess` (또는 필요한 권한만)
5. Create user
6. **Access Key ID와 Secret Access Key를 안전하게 저장**

### 4.3 AWS CLI 설정

```bash
aws configure

# 입력 정보:
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: ap-northeast-2  # 서울 리전
Default output format: json
```

**확인:**
```bash
aws sts get-caller-identity
```

출력 예시:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/terraform-user"
}
```

---

## 5. Terraform으로 인프라 구축

### 5.1 S3 버킷 생성 (Terraform State 저장용)

```bash
# S3 버킷 생성
aws s3 mb s3://myapp-terraform-state-<YOUR_NAME> --region ap-northeast-2

# 버전 관리 활성화
aws s3api put-bucket-versioning \
  --bucket myapp-terraform-state-<YOUR_NAME> \
  --versioning-configuration Status=Enabled
```

### 5.2 DynamoDB 테이블 생성 (State Lock용)

```bash
aws dynamodb create-table \
  --table-name terraform-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region ap-northeast-2
```

### 5.3 Terraform 변수 파일 생성

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars` 편집:
```hcl
aws_region   = "ap-northeast-2"
project_name = "myapp"
environment  = "prod"

# S3 버킷 이름 (위에서 생성한 것)
terraform_state_bucket = "myapp-terraform-state-<YOUR_NAME>"
```

### 5.4 Terraform 실행

```bash
cd terraform

# 초기화
terraform init

# 계획 확인 (어떤 리소스가 생성될지 확인)
terraform plan

# 인프라 생성 (약 10-15분 소요)
terraform apply
```

**중요한 출력 값 기록:**
```bash
# 출력 값 확인
terraform output

# 개별 출력 확인
terraform output ecr_backend_repository_url
terraform output ecr_frontend_repository_url
terraform output alb_dns_name
terraform output ecs_cluster_name
```

**출력 예시:**
```
ecr_backend_repository_url = "123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/myapp-backend"
ecr_frontend_repository_url = "123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/myapp-frontend"
alb_dns_name = "myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com"
ecs_cluster_name = "myapp-cluster"
```

---

## 6. GitHub 저장소 설정

### 6.1 GitHub 저장소 생성

1. GitHub에 로그인
2. New Repository 클릭
3. Repository 이름: `myapp-devops-demo`
4. Public 또는 Private 선택
5. Create repository

### 6.2 로컬 프로젝트를 GitHub에 Push

```bash
cd SoftBank

# Git 초기화 (이미 되어있으면 생략)
git init

# .gitignore 확인
# .gitignore에 다음 내용이 있는지 확인:
# backend/target/
# frontend/node_modules/
# frontend/build/
# terraform/.terraform/
# terraform/*.tfstate
# terraform/*.tfstate.backup
# *.tfvars

# 파일 추가
git add .

# 커밋
git commit -m "Initial commit"

# GitHub 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/myapp-devops-demo.git

# Push
git branch -M main
git push -u origin main
```

---

## 7. GitHub Actions 설정

### 7.1 GitHub Secrets 등록

1. GitHub Repository → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. 다음 Secrets 추가:

```
이름: AWS_ACCESS_KEY_ID
값: (IAM 사용자의 Access Key ID)

이름: AWS_SECRET_ACCESS_KEY
값: (IAM 사용자의 Secret Access Key)

이름: AWS_REGION
값: ap-northeast-2
```

### 7.2 워크플로우 파일 확인

`.github/workflows/` 디렉토리에 다음 파일들이 있는지 확인:
- `backend-ci-cd.yml`
- `frontend-ci-cd.yml`

필요시 파일 내용의 환경 변수를 수정:
```yaml
env:
  AWS_REGION: ap-northeast-2
  ECR_REPOSITORY: myapp-backend  # 또는 myapp-frontend
  ECS_SERVICE: myapp-backend-service
  ECS_CLUSTER: myapp-cluster
  CONTAINER_NAME: backend
```

---

## 8. 첫 배포 실행

### 8.1 코드 Push로 자동 배포

```bash
# 코드 수정 (예: README 수정)
echo "# MyApp" > README.md

# 커밋 및 Push
git add .
git commit -m "Trigger first deployment"
git push origin main
```

### 8.2 GitHub Actions 확인

1. GitHub Repository → Actions 탭
2. 워크플로우 실행 상태 확인
3. 실시간 로그 확인

**워크플로우 단계:**
1. ✅ Build and Test
2. ✅ Build Docker Image
3. ✅ Push to ECR
4. ✅ Deploy to ECS

### 8.3 배포 진행 상황 확인 (AWS Console)

#### ECS Service 확인
```bash
# CLI로 확인
aws ecs describe-services \
  --cluster myapp-cluster \
  --services myapp-backend-service \
  --region ap-northeast-2
```

또는 AWS Console:
1. ECS → Clusters → myapp-cluster
2. Services 탭 → myapp-backend-service
3. Deployments 탭에서 배포 상태 확인

#### CloudWatch Logs 확인
```bash
# 백엔드 로그
aws logs tail /ecs/myapp-backend --follow --region ap-northeast-2

# 프론트엔드 로그
aws logs tail /ecs/myapp-frontend --follow --region ap-northeast-2
```

---

## 9. 배포 확인

### 9.1 ALB DNS로 접속

```bash
# Terraform output에서 ALB DNS 확인
cd terraform
terraform output alb_dns_name
```

출력:
```
myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com
```

### 9.2 웹 브라우저에서 확인

```
# 프론트엔드
http://myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com

# 백엔드 Health Check
http://myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com/health

# 백엔드 API
http://myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com/api/users
```

### 9.3 curl로 테스트

```bash
# Health Check
curl http://myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com/health

# 사용자 목록
curl http://myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com/api/users

# 사용자 생성
curl -X POST http://myapp-alb-123456789.ap-northeast-2.elb.amazonaws.com/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","role":"Tester"}'
```

---

## 트러블슈팅

### 문제: Terraform apply 실패

**해결:**
1. AWS 자격 증명 확인:
```bash
aws sts get-caller-identity
```

2. IAM 권한 확인 (AdministratorAccess 필요)

3. 리전 확인:
```bash
aws configure get region
```

### 문제: GitHub Actions 실패

**해결:**
1. GitHub Secrets 확인
2. 워크플로우 로그 확인
3. ECR Repository가 존재하는지 확인:
```bash
aws ecr describe-repositories --region ap-northeast-2
```

### 문제: ECS Task가 시작되지 않음

**해결:**
1. Task Definition 확인
2. ECR 이미지가 존재하는지 확인
3. ECS Service 이벤트 확인:
```bash
aws ecs describe-services \
  --cluster myapp-cluster \
  --services myapp-backend-service \
  --region ap-northeast-2 \
  --query 'services[0].events'
```

### 문제: Health Check 실패

**해결:**
1. Security Group 규칙 확인
2. 컨테이너 로그 확인:
```bash
aws logs tail /ecs/myapp-backend --follow
```

3. Target Group Health Check 설정 확인

---

## 다음 단계

1. ✅ 로컬 개발 완료
2. ✅ AWS 인프라 구축 완료
3. ✅ CI/CD 파이프라인 구축 완료
4. ✅ 첫 배포 완료

**추가 작업:**
- [x] RDS MySQL 데이터베이스 연동
- [x] CodeDeploy Blue/Green 배포 설정
- [ ] 도메인 연결 (Route 53)
- [ ] HTTPS 설정 (ACM + ALB)
- [ ] Auto Scaling 튜닝
- [ ] CloudWatch 알람 설정
- [ ] 비용 모니터링

---

## 10. RDS MySQL 설정

RDS MySQL은 Terraform으로 자동 생성됩니다. 자세한 내용은 [RDS_SETUP_GUIDE.md](./RDS_SETUP_GUIDE.md)를 참조하세요.

### 주요 구성
- **DB 엔진**: MySQL 8.0
- **인스턴스**: db.t3.micro (프리 티어)
- **스토리지**: 20GB gp2
- **비밀번호**: AWS Secrets Manager에 자동 저장

### 확인 방법
```bash
# RDS 정보 확인
terraform output rds_endpoint
terraform output rds_address

# API로 데이터 확인
curl http://<ALB_DNS>/api/users
```

---

## 참고

- [README.md](./README.md) - 프로젝트 개요
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 배포 가이드
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결

---

## 완료!

모든 단계를 완료했다면 완전히 작동하는 DevOps 파이프라인이 구축된 것입니다!

**테스트:**
1. 코드 수정
2. Git Push
3. 자동 배포 확인
4. CodeDeploy Blue/Green 무중단 배포 확인
