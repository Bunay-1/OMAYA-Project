# Disaster Recovery and Resilience

Този документ описва основните Recovery Time Objective (RTO) и Recovery Point Objective (RPO) за OMAYA Platform.

## Цели за възстановяване

- **RTO (Recovery Time Objective):** до 1 час за критични услуги.
- **RPO (Recovery Point Objective):** до 15 минути за TimescaleDB телеметрия и Kafka събития.

## Ключови компоненти

- **TimescaleDB**: редовни бекъпи и snapshot-ове на PostgreSQL данните.
- **Kafka**: конфигурация с репликация и backup на ключови topics.
- **Redis**: периодично snapshot-ване на паметта и възстановяване от данни в Persistent Volume.
- **MinIO**: мулти-репликация за обемите с данни и отделни backup копия.
- **Vault**: secure unseal процедури, резервни ключове и рестор на secrets.

## Стратегии за възстановяване

1. **Регулярни бекъпи**
   - TimescaleDB snapshot и WAL архиви.
   - MinIO bucket репликация и offsite backup.
   - Kafka topic mirror/replication за критични потоци.

2. **Реплики и HA**
   - Използване на `docker-compose.ha.yml` за Kafka/Zookeeper кворум и многобройни нодове.
   - Използване на TimescaleDB с репликация за production deployment.

3. **Chaos testing и resilience**
   - Тестове за откази при Kafka outage, Redis outage и TimescaleDB failover.
   - Автоматизирани recovery сценарии да се вграждат в CI/QA pipeline.

4. **Документиран recovery план**
   - Тези процедури трябва да бъдат част от Production Runbook.
   - Възстановяване на platform state от snapshot след disaster.

## Мониторинг на възстановяването

- Следи се възстановяване на endpoint-ите и здравните проверки.
- Алгоритъм за автоматично рестартване на services с `restart: unless-stopped`.
- Нотификации при отклонения от допустими RTO/RPO граници.
