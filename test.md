הבנתי. זו ארכיטקטורה נכונה ובריאה הרבה יותר – ניהול חיבור (Connection Pool) יחיד ומרכזי לרדיס שמשמש כגשר בין ה-Backend ל-Frontend, במקום לפתוח חיבורים כפולים שרק יעמיסו על השרת.

במקרה כזה, אנחנו נשתמש בתבנית של **הזרקת תלויות (Dependency Injection)**. ניצור את הלוגר כך שהוא יקבל כפרמטר את הלקוח (Client) הקיים של רדיס.

כדי למנוע מעגליות ביבוא (Circular Imports) בשאר הקבצים בפרויקט, נגדיר את הלוגר תחת שם קבוע (למשל `ArcaneLogger`), כך שבכל קובץ אחר תוכל פשוט לקרוא ל-`logging.getLogger('ArcaneLogger')` ולקבל את הלוגר שכבר קונפג עם הרדיס.

### 1. קובץ הלוגר (`logger_setup.py`)

כאן נגדיר את ההנדלרים והפילטר, כשהפונקציה המרכזית מקבלת את אובייקט הרדיס שלך:

```python
import logging
from redis import Redis

class RedisFilter(logging.Filter):
    def filter(self, record):
        return getattr(record, 'to_redis', False)

class RedisHandler(logging.Handler):
    def __init__(self, redis_client: Redis, list_key: str = 'app_logs'):
        super().__init__()
        self.redis_client = redis_client
        self.list_key = list_key

    def emit(self, record):
        try:
            # מכיוון שהרדיס מקשר בין הבק לפרונט, לעיתים נוח יותר לאחסן 
            # את הלוג כמילון JSON מובנה (אפשר גם להשתמש ב-RedisJSON אם הפרויקט תומך), 
            # אבל למען הפשטות נשמור כאן כטקסט.
            log_entry = self.format(record)
            self.redis_client.rpush(self.list_key, log_entry)
        except Exception:
            self.handleError(record)

def init_project_logger(redis_client: Redis = None):
    # יצירת הלוגר המרכזי של הפרויקט
    logger = logging.getLogger('ArcaneLogger')
    logger.setLevel(logging.DEBUG)
    
    # כדי למנוע הוספה כפולה של הנדלרים אם קוראים לפונקציה פעמיים
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    # --- הנדלר לקונסולה (מקבל תמיד) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- חיבור הנדלר הרדיס ---
    if redis_client:
        try:
            # וידוא קליל שהקליינט שהוזרק אכן חי ומתקשר
            redis_client.ping()
            logger.info("Shared Redis client attached to ArcaneLogger successfully.")
            
            redis_handler = RedisHandler(redis_client)
            redis_handler.setLevel(logging.DEBUG)
            redis_handler.setFormatter(formatter)
            redis_handler.addFilter(RedisFilter())
            logger.addHandler(redis_handler)
            
        except Exception as e:
            logger.error(f"Failed to attach shared Redis client to logger. Console only fallback. Error: {e}")
    else:
        logger.warning("Logger initialized without a Redis client. Logs will only go to Console.")

    return logger

```

### 2. קובץ האתחול הראשי (למשל `main.py` או `app.py`)

כאן אתה מייבא את קליינט הרדיס המרכזי שלך שחי בנפרד, ומעביר אותו לפונקציית האתחול של הלוגר. זה קורה **פעם אחת** בזמן עליית האפליקציה:

```python
# יבוא הקליינט המרכזי שלך שחי בנפרד (שם הקובץ לדוגמה)
from my_shared_redis import my_redis_client 
from logger_setup import init_project_logger

# 1. אתחול הלוגר עם הרדיס הקיים (ידפיס לקונסולה שהחיבור הצליח)
logger = init_project_logger(redis_client=my_redis_client)

logger.info("App is starting up...")
logger.error("Failed to fetch initial state for frontend", extra={'to_redis': True})

```

### 3. שימוש בכל שאר הקבצים בפרויקט

בכל קובץ אחר שבו אתה כותב לוגיקה, אתה לא צריך להעביר שוב את הרדיס או לקרוא לפונקציית האתחול. אתה פשוט מושך את הלוגר הקיים מהזיכרון של פייתון:

```python
import logging

# שליפת הלוגר המקונפג
logger = logging.getLogger('ArcaneLogger')

def process_frontend_request(data):
    logger.debug("Processing request...") # ילך רק לקונסולה
    
    if not data:
        # ילך לקונסולה וגם יידחף לרשימה ברדיס הקיים
        logger.warning("Received empty data from frontend!", extra={'to_redis': True})

```
