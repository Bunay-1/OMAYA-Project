# История на промените (CHANGELOG)

Всички забележителни промени по този проект ще бъдат документирани в този файл.

## [3.1.0] - 2026-06-24

### Добавени
- Пълна актуализация на платформата до версия 3.1.0.
- Финализиране на всички фази от ROADMAP (Фази 1-4 са напълно изпълнени).
- Добавена нова Фаза 5 в ROADMAP: Production Hardening (Q3 2026).
- Добавен `SECURITY.md` с политика за сигурност и докладване на уязвимости.
- Актуализиран `CONTRIBUTING.md` с детайлни инструкции за Python, TypeScript и Rust.
- Почистване на документацията и синхронизиране на версиите във всички модули.
- Подобрена конфигурация на Docker за производствена среда.

## [3.0.1] - 2025-03-26

### Добавени
- Почистени неизползвани зависимости (@supabase/supabase-js).
- Синхронизирана версия на платформата във всички компоненти (v3.0.1).
- Обновена документация (README.md, ROADMAP.md, CHANGELOG.md).
- Добавен `CONTRIBUTING.md` на български език.
- Добавени шаблони за GitHub Issues и Pull Requests.
- Добавен ADR за Rust Edge конектори.
- Подобрена логика за mock данни във фронтенда.

## [3.0.0] - 2025-03-25

### Добавени - Фаза 4: Cloud Native & Scaling
- **Kubernetes Operator** (`k8s/operator/omaya_operator.py`) - Custom operator за управление на OMAYA deployments в Kubernetes
- **Kubernetes CRD** (`k8s/operator/crd.yaml`) - Custom Resource Definition за OMAYADeployment
- **Kubernetes RBAC** (`k8s/operator/rbac.yaml`) - Role-based access control за оператора
- **Kubernetes Deployment** (`k8s/operator/deployment.yaml`) - Deployment manifest за оператора
- **Multi-tenancy модул** (`backend/multi_tenancy.py`) - Поддръжка за множество организации с изолирани данни
- **Rust Edge конектори** (`edge-rust/`) - Високо-производителни конектори за edge устройства:
  - Modbus TCP/RTU конектор (`modbus_connector.rs`)
  - MQTT Sparkplug B конектор (`mqtt_sparkplug.rs`)
  - Store-and-Forward (`store_forward.rs`)
- **Global Deployment Automation** (`backend/global_deployment.py`) - Мулти-регионално разпространение и CI/CD автоматизация

### Променени
- Обновена версия на платформата на `3.0.0`
- Добавени нови зависимости за Kubernetes operator: kopf, kubernetes
- Добавени Rust зависимости за edge конектори: tokio, modbus, opcua, rumqttc, sqlx

### Документация
- Добавена документация за Kubernetes оператора
- Добавени примери за CRD и deployment конфигурации

## [2.5.0] - 2025-03-25

### Добавени - Фаза 1: Индустриална свързаност и Edge Layer
- Пълна имплементация на Siemens S7-1200/1500 конектор (`backend/adapters/s7_connector.py`)
- Пълна имплементация на Fanuc FOCAS конектор (`backend/adapters/fanuc_focas.py`)
- Пълна имплементация на Modbus TCP/RTU конектор (`backend/adapters/modbus.py`)
- Пълна имплементация на OPC-UA конектор (`backend/adapters/opc_ua.py`)
- Store-and-Forward механизъм с SQLite буфер (`backend/store_and_forward.py`)
- MQTT Sparkplug B поддръжка за IoT съобщения (`backend/mqtt_sparkplug.py`)

### Добавени - Фаза 2: Enterprise Testing & Quality Assurance
- Security hardening модул за production (`backend/security_hardening.py`)
- Performance optimization модул (`backend/performance_optimization.py`)
- Hardware-in-the-Loop тестове за индустриални адаптери
- Разширени тестове за всички нови модули (100+ теста)

### Добавени - Фаза 3: AI/ML Оптимизация и XAI
- Online Learning v2.0 с drift detection (`backend/online_learning_v2.py`)
- Multi-modal Fusion за комбиниране на данни (`backend/multi_modal_fusion.py`)
- Explainable AI UI компонент (вече съществуващ)

### Добавени - Тестове
- `test_s7_connector.py` - 15+ теста за Siemens S7 конектор
- `test_fanuc_focas.py` - 15+ теста за Fanuc FOCAS конектор
- `test_store_and_forward.py` - 12+ теста за Store-and-Forward
- `test_mqtt_sparkplug.py` - 15+ теста за MQTT Sparkplug B
- `test_hil_s7.py` - 12+ Hardware-in-the-Loop тестове за S7
- `test_hil_modbus.py` - 12+ Hardware-in-the-Loop тестове за Modbus
- `test_security_hardening.py` - 10+ теста за security
- `test_performance_optimization.py` - 12+ теста за performance
- `test_online_learning.py` - 8+ теста за online learning
- `test_multi_modal_fusion.py` - 10+ теста за multi-modal fusion

### Променени
- Обновена версия на платформата на `2.5.0`
- Добавени нови зависимости в `requirements.txt`: python-snap7, pymodbus, asyncua, paho-mqtt, cryptography, hvac

## [2.4.8] - 2025-03-24

### Добавени
- Мащабно разширяване на бекенд тестовете (50+ нови случая).
- Тестове за гранични случаи в AI моделите (LSTM, RUL, Anomaly Detection).
- Задълбочени тестове за агрегацията на данни и обработката на Kafka потоци.
- Юнит тестове за фронтенд компоненти: `PredictiveMaintenancePanel`, `ToolWearTracker` и `MaintenanceCalendar`.
- Подобрен `.gitignore` файл за по-чисто хранилище.

### Поправени
- Премахната е нестабилната E2E конфигурация с Playwright поради несъвместимост с текущата среда.

### Променени
- Обновена версия на платформата на `2.4.8`.

## [2.4.7] - 2025-03-24

### Добавени
- GitHub Actions CI пайплайн за автоматизирано тестване и линтване.
- GitHub Actions CD пайплайн за автоматизирано изграждане и публикуване на Docker изображения.
- Глобален компонент `ErrorBoundary` във фронтенда за прихващане на грешки при рендериране.
- Поддръжка за сервизни контейнери (Redis, TimescaleDB) в CI средата за реални интеграционни тестове.

### Променени
- Обновена версия на платформата на `2.4.7`.

## [2.4.6] - 2025-03-24

### Добавени
- Юнит тестове за напреднали AI модули: `drift_detection`, `online_learning` и `explainable_ai`.
- Юнит тестове за индустриални адаптери (`modbus`, `opc_ua`, `s7_connector`).
- Юнит тестове за Data Lake интеграцията.
- Комплексни интеграционни тестове за целия поток на данни (`telemetry -> aggregator -> cache`).
- Юнит тестове за фронтенд компоненти: `Sidebar`, `FleetOverview` и `MachineDetailPanel`.
- Тестове за custom hook `useRealTimeData`.

### Променени
- Оптимизирано кеширане на слоеве в Dockerfile за по-бързо изграждане.
- Обновена версия на платформата на `2.4.6`.

## [2.4.5] - 2025-03-24

### Добавени
- Юнит тестове за модулите `auth`, `rate_limiter`, `websocket_manager` и `ai_models`.
- Юнит тестове за фронтенд компонента `AlertsPanel`.
- Поддръжка за TLS криптиране в бекенда (HTTPS) на порт 8443.
- Автоматично генериране на self-signed сертификати в дев среда.
- Защитни HTTP хедъри (Security Hardening Headers) в middleware слоя.
- Йерархична ролева система (RBAC hierarchy) в модула за ауторизация.

### Поправени
- Поправена логиката за проверка на пермисии в `AuthManager.has_permission` за поддръжка на йерархия.
- Поправени mock данни в `fake_users_db` за коректна проверка на пароли.

### Променени
- Обновена версия на платформата на `2.4.5`.

## [2.4.4] - 2025-03-24

### Добавени
- Глобално обработване на грешки (Global Error Handling) в бекенда.
- Структурирано логване (Structured Logging) в JSON формат.
- Тестова инфраструктура за фронтенда с Vitest и React Testing Library.
- Юнит тестове за фронтенд компоненти (KPICards).
- Конфигурация за E2E тестове с Playwright.
- Интеграционни тестове за TimescaleDB.

### Променени
- Оптимизиран Dockerfile за бекенда чрез multi-stage build.
- Обновена версия на платформата на `2.4.4`.

## [2.4.3] - 2025-03-24

### Добавени
- Интеграционни тестове за Redis, Kafka и Data Lake (MinIO).
- Юнит тестове за модула Audit Trails.
- Реализирани реални здравни проверки (health checks) за Redis, AI модели, Kafka и Data Lake в `/api/self-test`.
- Поддръжка на променливи на средата за `ALLOWED_ORIGINS` в CORS конфигурацията.

### Поправени
- Липсващ `import time` и `import os` в `main.py`.
- Поправена CORS конфигурация - премахнато рисковото `allow_origins=["*"]` и заменено с конфигурируем списък чрез променливи на средата.
- Премахнати твърдо зададени (hardcoded) пароли и имена на контейнери в `docker-compose.yml` за по-добра сигурност и мащабируемост.
- Добавени липсващи атрибути `model` в `LSTMPredictor` и `RULPredictor` класовете за съвместимост с SHAP/LIME обясненията.

### Променени
- Обновена версия на платформата на `2.4.3`.

## [2.4.2] - 2025-03-24

### Добавени
- Инсталиран `curl` в Docker изображенията за бекенда и фронтенда за по-надеждни здравни проверки (healthchecks).
- Добавено лого на `curl` в технологичния стек в `README.md`.

### Поправени
- Коригиран проблем със стартирането на Docker контейнерите, причинен от неуспешни здравни проверки (healthchecks). Предишният метод разчиташе на библиотека `requests` в Python, която не беше налична във всички изображения.
- Актуализирани конфигурациите в `docker-compose.yml` и съответните му варианти (`.dev.yml`, `.prod.yml`, `.ha.yml`, `.small.yml`, `.standard.yml`) да използват `curl` за здравни проверки.

### Променени
- Пълно ребрандиране на платформата от "OMAYA Fleet Monitoring" на "OMAYA Fleet Monitoring".
- Актуализирана поддръжката и авторските права към DefComs.
- Преразглеждане на техническите твърдения в документацията за по-голям реализъм — преминаване към статус "Release Candidate (v2.4-RC)".
- Добавени конкретни KPI показатели за AI моделите (Accuracy: 93.2%, Precision: 91.4% и др.).
- Разширена документация за Edge Layer и индустриална свързаност (MQTT, OPC-UA, Modbus, Siemens S7, Fanuc FOCAS, Heidenhain LSV2).
- Добавени механизми за Edge устойчивост: Store-and-Forward и конфликтна резолюция (LWW).
- Добавени критични предупреждения за сигурност относно използването на пароли по подразбиране.
- Публикуван стратегически план за развитие в `ROADMAP.md`.
- Добавени базов скелет за индустриални адаптери в `backend/adapters/` (OPC-UA, Modbus, Siemens S7).
- Пълно преработване на High Availability (HA) архитектурата в `docker-compose.ha.yml`:
    - Имплементиран Zookeeper кворум (3 възела) и Kafka клъстер (3 брокера).
    - Добавен Nginx Load Balancer за разпределяне на трафика към API и фронтенда.
    - Премахнати hardcoded пароли и въведени променливи на средата.
    - Фиксирани версии на всички Docker изображения (премахнати `latest` тагове).
- Обновена версия на платформата от `2.4.1` на `2.4.2` във всички компоненти:
    - `package.json`
    - `backend/main.py`
    - `README.md`
    - `src/components/dashboard/Dashboard.tsx`
    - Всички файлове в директория `Docs/`
- Актуализирана документацията и датите на последна промяна (Март 2025).
