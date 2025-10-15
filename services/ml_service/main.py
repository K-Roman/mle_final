import time
from fastapi import FastAPI
from handler import FastApiHandler
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge

# создаём экземпляр FastAPI-приложения
app = FastAPI()

# создаём обработчик запросов для API
app.handler = FastApiHandler()

# инициализируем и запускаем экпортёр метрик
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

REQUEST_COUNTER = Counter(
    "model_requests_total", 
    "Total number of prediction requests",
)
PREDICTION_ERRORS = Counter(
    "prediction_errors_total",
    "Total number of prediction errors"
)
INFERENCE_LATENCY = Gauge(
    "inference_latency_seconds",
    "Time taken to generate a prediction",
)
PREDICTED_PRODUCT_COUNT = Gauge(
    "predicted_products_count",  # ← лучше переименовать
    "Number of predicted products",  # ← и описание
)

@app.get("/")
def health_check():
    return {"status": "OK"} 

@app.post("/api/products/") 
def get_prediction(user_id: int, model_params: dict):
    """Функция для получения рекомендованных продуктов"""
    REQUEST_COUNTER.inc()
    start_time = time.time()  # ← засекаем время
    
    try:
        all_params = {
            "user_id": user_id,
            "model_params": model_params
        }
        prediction = app.handler.handle(all_params)
        
        # Записываем время выполнения
        processing_time = time.time() - start_time
        INFERENCE_LATENCY.set(processing_time)  # ← используем .set()
        
        # Записываем количество продуктов
        product_count = len(prediction.get("products", []))
        PREDICTED_PRODUCT_COUNT.set(product_count)  # ← используем .set()
        
        return prediction
        
    except Exception as e:
        PREDICTION_ERRORS.inc()
        raise