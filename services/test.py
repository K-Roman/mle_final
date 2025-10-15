import requests
import time
import random
import json

# Базовые параметры
base_url = "http://127.0.0.1:8081/api/products/"
headers = {"Content-Type": "application/json"}

# Отправляем 40 запросов
for i in range(40):
    # Генерируем случайные параметры (можно раскомментировать ваш вариант)
    params = {
                    "fecha_dato": "2016-05-28",
            "ncodpers": 1375586,
            "ind_empleado": "N",
            "pais_residencia": "ES",
            "sexo": "H",
            "age": random.randint(18, 50),
            "fecha_alta": "2015-01-12",
            "ind_nuevo": 0.0,
            "antiguedad": 16,
            "indrel": 1.0,
            "ult_fec_cli_1t": None,
            "indrel_1mes": "1.0",
            "tiprel_1mes": "A",
            "indresi": "S",
            "indext": "N",
            "conyuemp": None,
            "canal_entrada": "KHL",
            "indfall": "N",
            "tipodom": 1.0,
            "cod_prov": 29.0,
            "nomprov": "MALAGA",
            "ind_actividad_cliente": 1.0,
            "renta": random.randint(50000, 100000),
            "segmento": "02 - PARTICULARES",
    }
    
    # Отправляем POST-запрос
    try:
        response = requests.post(
            url=f"{base_url}?user_id={i}",
            headers=headers,
            data=json.dumps(params)  # Преобразуем dict в JSON-строку
        )
        
        print(f"Запрос {i}: Status {response.status_code}, Response: {response.text}")
        
    except Exception as e:
        print(f"Ошибка при запросе {i}: {str(e)}")
    
    # Паузы по условиям
    if i == 30:
        time.sleep(30)
    time.sleep(2)
