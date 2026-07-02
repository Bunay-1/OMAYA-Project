# 🔧 OMAYA Fleet Monitoring Platform

<div align="center">

[![CI/CD Status](https://github.com/Bunay-1/OMAYA-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/Bunay-1/OMAYA-Project/actions)

<img src="https://defcoms.eu/images/DefComs-logo.svg" width="250" alt="DefComs Logo" />

![Platform Status](https://img.shields.io/badge/Status-Production%20Ready%20(v3.1.6)-green?style=for-the-badge&logo=react)
![Version](https://img.shields.io/badge/Version-3.1.6-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-Enterprise-red?style=for-the-badge)

**Корпоративна IoT/IIoT архитектура за OMAYA Fleet Management с AI-базирана превантивна поддръжка**

[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.2-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-FF6F00?style=flat-square&logo=tensorflow)](https://www.tensorflow.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes)](https://kubernetes.io/)
[![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka)](https://kafka.apache.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis)](https://redis.io/)
[![Rust](https://img.shields.io/badge/Rust-000000?style=flat-square&logo=rust)](https://www.rust-lang.org/)

</div>

---

## 📋 Съдържание

- [🎯 Обзор на платформата](#-обзор-на-платформата)
- [🚀 Ключови функции](#-ключови-функции)
- [🏗️ Архитектура](#️-архитектура)
- [🛠️ Технологичен стек](#️-технологичен-стек)
- [📦 Инсталация и настройка](#-инсталация-и-настройка)
- [🎨 Фронтенд модули](#-фронтенд-модули)
- [⚙️ Бекенд модули](#️-бекенд-модули)
- [🤖 AI/ML възможности](#-aiml-възможности)
- [📊 API документация](#-api-документация)
- [🔒 Сигурност](#-сигурност)
- [📈 Мониторинг и обсервабилност](#-мониторинг-и-обсервабилност)
- [🌍 Deployment](#-deployment)
- [🧪 Тестване](#-тестване)
- [📚 Документация](#-документация)
- [💼 Business и гростратегия](#-business-и-гростратегия)
- [✅ Compliance и стандарти](#-compliance-и-стандарти)
- [🔁 Release & DevOps процеси](#-release--devops-процеси)
- [🎯 Статистика на платформата](#-статистика-на-платформата)
- [🗺️ Пътна карта (Roadmap)](#️-пътна-карта-roadmap)
- [🤝 Поддръжка](#-поддръжка)

---

## 🎯 Обзор на платформата

**OMAYA Fleet Monitoring Platform** е цялостно корпоративно решение, предназначено за мониторинг в реално време, превантивна поддръжка и интелигентно управление на индустриални машини. Изградена с модерни технологии и AI анализи, тя позволява на производителите да оптимизират операциите, да намалят престоите и да увеличат производителността чрез инсайти, базирани на данни.

### Възможности на платформата

- **Мониторинг на флота в реално време** - Наблюдение на 120+ машини в множество производствени зони (Siemens, Fanuc, Heidenhain).
- **Индустриална свързаност** - Интегрирани MQTT, OPC-UA и Modbus TCP/RTU за събиране на данни от PLC.
- **AI-базирана превантивна поддръжка** - TensorFlow LSTM модели предсказват повреди преди те да се случат.
- **RAG Knowledge Base** - Интелигентно извличане на документи и обучение на системата чрез семантично търсене (v3.1.6).
- **Визуална инспекция (YOLO)** - Качествен контрол и детекция на дефекти в реално време (v3.1.6).
- **Стрийминг на телеметрия** - Автоматично опресняване през WebSockets с ниска латентност.
- **Разширени анализи** - SHAP/LIME обяснимост, детекция на дрифт на моделите, онлайн обучение.
- **Корпоративна интеграция** - Глобален deployment, одитни записи, data lake, управление на тайни.
- **Пълен мониторинг** - Prometheus, Grafana, Alertmanager с персонализирани табла.

### Статус на платформата

```
🚀 Версия: v3.1.6 - Production Ready
🟢 Ядрени системи: Оперативни (Real-time Database + Auth)
🔒 Сигурност: Подсилена архитектура (RBAC + DB Auth)
📊 Мониторинг: Активен в реално време
🤖 AI модели: Внедрени (Real TensorFlow/SKLearn Models)
```

---

## 🚀 Ключови функции

### 🏭 Основни функции

| Функция | Описание | Статус |
|---------|----------|--------|
| **Мониторинг в реално време** | Наблюдение на 120+ машини в 6 зони с актуализации на живо | ✅ Завършено |
| **RAG Knowledge Base** | Интелигентна база знания с поддръжка на PDF, DOCX, ODT и др. | ✅ Завършено |
| **Visual Inspection (YOLO)** | Детекция на дефекти чрез компютърно зрение | ✅ Завършено |
| **Телеметрия на живо** | WebSocket стрийминг на сензорни данни с 3-секунден интервал | ✅ Завършено |
| **KPI показатели** | OEE, Uptime, Defect Rate, Throughput, MTBF, MTTR | ✅ Завършено |
| **Управление на аларми** | Многостепенни аларми с работни процеси за ескалация | ✅ Завършено |
| **Следене на инструменти** | Мониторинг на износването и предсказване на замяна | ✅ Завършено |
| **Календар за поддръжка** | График за превантивна и предиктивна поддръжка | ✅ Завършено |
| **Прогнозиране на производството** | AI прогнози с доверителни интервали | 🏗️ В процес |

### 🤖 AI & Machine Learning

| Функция | Описание | Статус |
|---------|----------|--------|
| **TensorFlow LSTM** | Невронна мрежа за предсказване на повреди в тайм-серии | ✅ Завършено |
| **Ensemble RUL Models** | Random Forest + Gradient Boosting за оставащ полезен живот | ✅ Завършено |
| **Онлайн обучение** | Адаптивна детекция на аномалии с непрекъснато подобрение | ✅ Завършено |
| **Детекция на дрифт** | Мониторинг на точността (PSI) с автоматично преобучение | ✅ Завършено |
| **AI Explainability** | SHAP & LIME анализи за интерпретируемост на моделите | ✅ Завършено |
| **Training Pipeline** | Автоматизиран процес на обучение с контрол на версиите | 🏗️ В процес |
| **Edge Computing** | ONNX конвертиране за работа в периферията | ✅ Завършено |

### ⚙️ Бекенд инфраструктура

| Функция | Описание | Статус |
|---------|----------|--------|
| **FastAPI** | Високопроизводително API с автоматична документация | ✅ Завършено |
| **WebSocket** | Двупосочна комуникация за данни в реално време | ✅ Завършено |
| **Kafka Streaming** | Event-driven архитектура за телеметрия и аларми | ✅ Завършено |
| **Redis Cache** | Интелигентно кеширане за мигновени отговори | ✅ Завършено |
| **TimescaleDB** | Специализирана база данни за времеви редове | ✅ Завършено |
| **GraphQL API** | Гъвкави заявки за данни чрез Strawberry GraphQL | ✅ Завършено |
| **Rate Limiting** | Защита на API чрез Redis-базирани лимити | ✅ Завършено |

### 🏢 Корпоративни функции

| Функция | Описание | Статус |
|---------|----------|--------|
| **Multi-Region Deployment** | Глобална архитектура с автоматичен failover | 🏗️ В процес |
| **Одитни записи** | Логване за съответствие с SHA-256 верификация | ✅ Завършено |
| **Data Lake** | MinIO S3 за дългосрочно съхранение на архивни данни | ✅ Завършено |
| **Vault Secrets** | Сигурно съхранение на ключове и пароли | ✅ Завършено |
| **TLS 1.3 Криптиране** | Защита на всички комуникации | ✅ Завършено |
| **Service Mesh** | Istio/Linkerd конфигурация за микроуслуги | 🏗️ В процес |
| **PLC Интеграция** | Поддръжка за Siemens S7, Fanuc FOCAS, Modbus | ✅ Завършено |
| **Индустриални протоколи** | Пълен стек: MQTT, OPC-UA, Modbus TCP/RTU | ✅ Завършено |

### 📊 Мониторинг и Операции

| Функция | Описание | Статус |
|---------|----------|--------|
| **Prometheus Metrics** | Обсервабилност с 20+ потребителски метрики | ✅ Завършено |
| **Alertmanager** | Маршрутизация и групиране на известия | ✅ Завършено |
| **Grafana Dashboards** | Готови табла за флот, машини, AI и производителност | ✅ Завършено |
| **Kubernetes Deployment** | Helm чартове с HPA (Horizontal Pod Autoscaling) | ✅ Завършено |
| **Здравни проверки** | Автоматизирана диагностика на всички подсистеми | ✅ Завършено |

### 🧪 Качество и Тестване

| Функция | Описание | Статус |
|---------|----------|--------|
| **Pytest Suite** | 241+ тест случая за пълно покритие на логиката | ✅ Завършено |
| **CI/CD Pipeline** | GitHub Actions за автоматизирано тестване и деплой | ✅ Завършено |
| **HIL Симулатори** | Hardware-in-the-Loop симулация за индустриални протоколи | ✅ Завършено |
| **Playwright E2E** | Визуална верификация на фронтенда | ✅ Завършено |

---

## 🏗️ Архитектура

### Индустриална интеграция (Edge)

Платформата OMAYA разполага с мощен Edge слой за директна връзка с производството:

- **Протоколни адаптери**:
    - **OPC-UA**: За модерни контролери и унифицирано моделиране на данни.
    - **Modbus TCP/RTU**: За наследен хардуер и специализирани сензори.
    - **MQTT (Sparkplug B)**: За ефикасен индустриален обмен на съобщения.
- **PLC Интеграция**:
    - **Siemens S7**: Директна връзка с S7-1200/1500 чрез RFC1006.
    - **Fanuc FOCAS**: Дълбока интеграция за данни от CNC машини.
- **Edge Processing**: ONNX-базирана дедукция за детекция на аномалии на място.

### Docker услуги (13 контейнера)

1.  **omaya-frontend** → React UI (Nginx)
2.  **omaya-api** → FastAPI Backend
3.  **omaya-redis** → Cache Layer
4.  **omaya-kafka** → Event Streaming
5.  **omaya-zookeeper** → Kafka Coordination
6.  **omaya-schema-registry** → Kafka Schema Management
7.  **omaya-timescaledb** → Time-series Database
8.  **omaya-prometheus** → Metrics Collection
9.  **omaya-alertmanager** → Alert Processing
10. **omaya-grafana** → Visual Analytics
11. **omaya-redis-exporter** → Redis Monitoring
12. **omaya-node-exporter** → System Metrics
13. **omaya-minio** → Data Lake / S3 Storage

---

## 🛠️ Технологичен стек

### Фронтенд технологии

| Технология | Версия | Цел | Лого |
|------------|---------|-----|------|
| **React** | 18.2.0 | UI Framework | ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react) |
| **TypeScript** | 5.8.2 | Типизация | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript) |
| **Vite** | 7.1.12 | Build Tool | ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite) |
| **TailwindCSS** | 3.4.1 | Стилизация | ![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss) |
| **Framer Motion** | 11.18.0 | Анимации | ![Framer Motion](https://img.shields.io/badge/Framer%20Motion-FF69B4?style=flat-square) |
| **Recharts** | 3.7.0 | Визуализация | ![Recharts](https://img.shields.io/badge/Recharts-FF6B6B?style=flat-square) |

### Бекенд & AI технологии

| Технология | Версия | Цел | Лого |
|------------|---------|-----|------|
| **Python** | 3.10+ | Runtime | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python) |
| **FastAPI** | 0.109.0 | Web Framework | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi) |
| **TensorFlow** | 2.15.0 | Deep Learning | ![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow) |
| **Kafka** | 2.0.2 | Стрийминг | ![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka) |
| **Redis** | 5.0.1 | Кеширане | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis) |
| **TimescaleDB** | Latest | Time-series DB | ![TimescaleDB](https://img.shields.io/badge/TimescaleDB-0082C9?style=flat-square&logo=postgresql) |

---

## 📦 Инсталация и настройка

### Предпоставки
- Docker & Docker Compose
- Node 20+ и npm/yarn за фронтенд
- Python 3.10+ за бекенд (локално)

### Бърз старт (с Docker Compose)
1. Клонирайте хранилището:
```bash
git clone https://github.com/Bunay-1/OMAYA-Project.git
cd OMAYA-Project
```
2. Създайте `.env` от примера и попълнете стойностите:
```bash
cp .env.example .env
# Edit .env and replace __REPLACE_ME__ values
```
3. Стартирайте услугите:
```bash
docker-compose up -d --build
```
4. Достъп до услугите:
- UI: http://localhost
- API Docs (Swagger): http://localhost:8000/docs
- Grafana: http://localhost:3001

### Разработка локално (без Docker)
1. Backend:
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cp .env.example backend/.env   # optional: use env vars instead
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
2. Frontend:
```bash
cd src
npm install
npm run dev
```

### Troubleshooting
- Ако някоя услуга не стартира, проверете логовете: `docker-compose logs -f`.
- Уверете се, че всички `__REPLACE_ME__` стойности в `.env` са попълнени.

---

## 🤖 AI/ML възможности

### RAG Knowledge Base (v3.1.6)
Интелигентна база знания за семантично търсене в техническа документация.
- **Поддържани формати:** PDF, DOCX, ODT, PPTX, XLSX, JSON, XML, CSV, TXT, MD.
- **Технологии:** LangChain, FAISS, HuggingFace (all-MiniLM-L6-v2).

### Visual Inspection YOLO (v3.1.6)
Детекция на дефекти в реално време чрез YOLO за качествен контрол на производствената линия.

---

## 📊 API документация

### OpenAPI / Swagger
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI spec**: http://localhost:8000/openapi.json
- **Postman collection**: вижте `Docs/API_REFERENCE.md` или поисквайте в support.

### Здраве и Статус
```http
GET /api/v1/health HTTP/1.1
Host: localhost:8000
```
**Отговор:**
```json
{
  "service": "OMAYA Fleet Monitoring API",
  "version": "3.1.6",
  "status": "operational"
}
```

---

## 🎯 Статистика на платформата (v3.1.6)

| Метрика | Брой/Стойност |
|---------|---------------|
| **Python модули** | 35+ |
| **React компоненти** | 45+ |
| **Docker услуги** | 13 |
| **API ендпоинти** | 55+ |
| **Тестови случаи** | 241+ |
| **Точност на AI** | 93.2% |

### Зрялост на платформата
```
Основни функции:        ████████████████████ 100%
Бекенд услуги:          ████████████████████ 100%
AI/ML модели:           ██████████████████░░ 90%
RAG & YOLO:             ████████████████████ 100%
Сигурност:              ████████████████████ 100%
Тестване:               ████████████████████ 100%
Документация:           ████████████████████ 100%
```

---

## 🗺️ Пътна карта (Roadmap)
Вижте пълния [ROADMAP.md](./ROADMAP.md) за детайли по Q3 2026.

---

## 💼 Business и гростратегия
- **Enterprise self-hosted и cloud опции** за големи заводи и индустриални паркове.
- **Pricing & tiers**: contact support for customized enterprise pricing, pilot projects and trial proposals. See [Docs/PRICING.md](./Docs/PRICING.md) for example options.
- **Pilot/demo**: hosted sandbox evaluations и read-only trial deployment могат да бъдат договорени чрез support.
- **ROI proof points**: намаляване на downtime, подобряване на OEE и навременна превантивна поддръжка.
- **Case study hints**: примерни KPI резултати могат да бъдат включени като част от enterprise demo.

## ✅ Compliance и стандарти
- В процес на подготовка за **ISO 27001** и **IEC 62443** сертификация.
- Архивиране и ретеншън политика за GDPR и преработка на индустриални данни.
- Изграждане на accessibility roadmap за WCAG съвместимост.
- Доказателство за безопасност и enterprise readiness чрез `SECURITY.md`, [Docs/DISASTER_RECOVERY.md](./Docs/DISASTER_RECOVERY.md) и [Docs/MODEL_GOVERNANCE.md](./Docs/MODEL_GOVERNANCE.md).

## 📺 Demo и UX onboarding
- Preview на dashboard с ключови KPI, alerts и AI insights.
- Non-developer quick-start: contact support for a tailored operations onboarding session.
- Sandbox / read-only demo среда може да се заяви чрез support.

### Screenshots / Demo

If you want to include a visual demo, add a screenshot at `Docs/demo-screenshot.png` and it will be displayed here. Example screenshots help new users see the UI and main dashboards quickly.


## 🔁 Release & DevOps процеси
- Готови за автоматична release notes генерация с GitHub Actions `release.yml`.
- Автоматичен dependency scanning чрез `dependabot.yml` за npm, pip, GitHub Actions и Docker.
- Документация за процеса: [Docs/RELEASE_PROCESS.md](./Docs/RELEASE_PROCESS.md).
- Препоръчва се `main` branch protection с изискване на статус проверките:
  - `backend-tests`
  - `frontend-build`
  - `security-scan`
  - `Run pre-commit`

---

## 🤝 Поддръжка
- **Issues:** [Bunay-1/OMAYA-Project/issues](https://github.com/Bunay-1/OMAYA-Project/issues)
- **Email:** support@defcoms.eu
- **Hosted demo / POC request:** contact support for evaluation access.

---

## 📸 Dashboard preview
![OMAYA Dashboard Preview](https://via.placeholder.com/1200x600.png?text=OMAYA+Dashboard+Preview)

Наличието на демонстрационен dashboard прави платформата по-достъпна за operations и production management екипи.

---

---
**Версия:** 3.1.6 | **Статус:** 🟢 Production Ready | **Последна актуализация:** 25.06.2026
**Поддържа се от:** DefComs
