from context import Context
import json
import importlib.util
import os
import redis
import time
from zipfile import ZipFile

# Load environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_INPUT_KEY = os.getenv("REDIS_INPUT_KEY", None)
REDIS_OUTPUT_KEY = os.getenv("REDIS_OUTPUT_KEY", None)
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", 5))
ZIP_FILE_PATH = os.getenv("ZIP_FILE_PATH", "")
FUNCTION_HANDLER = os.getenv("FUNCTION_HANDLER", "handler")

# Checking if crucial environment variables are set
if not REDIS_INPUT_KEY:
    raise Exception("REDIS_INPUT_KEY is not set")
if not REDIS_OUTPUT_KEY:
    raise Exception("REDIS_OUTPUT_KEY is not set")

# Connect to Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)

# Load user function
def load_user_function():
    if ZIP_FILE_PATH:
        with ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
            zip_ref.extractall("/tmp/user_code")
        spec = importlib.util.spec_from_file_location("user_module", "/tmp/user_code/handler.py")
    else:
        spec = importlib.util.spec_from_file_location("user_module", "/app/handler.py")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, FUNCTION_HANDLER)

# Monitor and process data
def monitor(handler: callable, context: Context):
    while True:
        usage_data = None
        user_output = None
        try:
            usage_data = redis_client.get(REDIS_INPUT_KEY)
        except Exception as e:
            print(f"Error getting data from Redis: {e}")
            time.sleep(MONITORING_INTERVAL)
            continue

        if not usage_data:
            print("No data found in Redis")
            time.sleep(MONITORING_INTERVAL)
            continue

        try:
            usage_data = json.loads(usage_data)
            user_output = handler(usage_data, context)
        except Exception as e:
            print(f"Error processing data: {e}")
            time.sleep(MONITORING_INTERVAL)
            continue

        try:
            redis_client.set(REDIS_OUTPUT_KEY, json.dumps(user_output))
            context.update_last_execution()
        except Exception as e:
            print(f"Error saving data to Redis: {e}")
            time.sleep(MONITORING_INTERVAL)
            continue

        time.sleep(MONITORING_INTERVAL)


try:
    handler = load_user_function()
except Exception as e:
    raise Exception(f"Error loading user function: {e}")

context = Context(host=REDIS_HOST, port=REDIS_PORT, input_key=REDIS_INPUT_KEY, output_key=REDIS_OUTPUT_KEY)

monitor(handler=handler, context=context)
