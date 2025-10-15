# Структура проекта
```bash
mle_final/
├── data/
│   └── df_long_cumsum.parquet
├── models/
│   └── dict_encoders.pkl
├── services/
│   ├── data/ # дополнительные данные         
│   ├── ml_service/   
│   ├── mlflow_server/   
│   ├── models/
│   ├── notebooks/ # ноутбуки с EDA, экспериментами
│   ├── prometheus/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   └── test.py
├── Instructions.md
├── Monitoring.md
└── README.md
```

# Инструкции по запуску микросервиса

Если необходимо перейти в поддиректорию, напишите соответсвтующую команду

## 1. FastAPI микросервис

```python
# команды создания виртуального окружения
cd mle_final
python -m venv venv
source venv/bin/activate

# и установки необходимых библиотек в него
cd services
pip install -r requirements.txt


# команда запуска docker
docker compose up --build
```

### Пример curl-запроса к микросервису

```bash
curl -X POST "http://127.0.0.1:8081/api/products/?user_id=1375586"   -H "Content-Type: application/json"   -d '{"fecha_dato": "2016-05-28","ncodpers": 1375586,"ind_empleado": "N","pais_residencia": "ES","sexo": "H","age": 36,"fecha_alta": "2015-01-12","ind_nuevo": 0.0,"antiguedad": 16,"indrel": 1.0,"ult_fec_cli_1t": null,"indrel_1mes": "1.0","tiprel_1mes": "A","indresi": "S","indext": "N","conyuemp": null,"canal_entrada": "KHL","indfall": "N","tipodom": 1.0,"cod_prov": 29.0,"nomprov": "MALAGA","ind_actividad_cliente": 1.0,"renta": 87218.1,"segmento": "02 - PARTICULARES"}'
```

## 4. Скрипт симуляции нагрузки
Скрипт генерирует 40 запросов
mle_final/services/test.py

```
# команды необходимые для запуска скрипта
python3 test.py
```

Адреса сервисов:
- микросервис: http://localhost:8081
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000