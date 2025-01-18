from context import Context
import json
import importlib.util
import os
import redis
import time

# Load environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_INPUT_KEY = os.getenv("REDIS_INPUT_KEY", None)
REDIS_OUTPUT_KEY = os.getenv("REDIS_OUTPUT_KEY", None)
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", 5))
MAIN_FILE_NAME = os.getenv("MAIN_FILE_NAME", "resource_usage")
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
def load_user_function(main_file_path: str):
    spec = importlib.util.spec_from_file_location("user_module", main_file_path)
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

main_file_path = f"/app/serverless_function/{MAIN_FILE_NAME}.py"
try:
    handler = load_user_function(main_file_path=main_file_path)
except Exception as e:
    raise Exception(f"Error loading user function: {e}")

context = Context(
    host=REDIS_HOST,
    port=REDIS_PORT,
    input_key=REDIS_INPUT_KEY,
    output_key=REDIS_OUTPUT_KEY,
    main_file_path=main_file_path,
)

monitor(handler=handler, context=context)
