import os
import datetime


class Context(object):
    host = None
    port = None
    input_key = None
    output_key = None
    last_execution = None
    env = None

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        input_key: str = "metrics",
        output_key: str = "some_output",
        main_file_path: str = "/app/handler.py",
    ):
        self.host = host
        self.port = port
        self.input_key = input_key
        self.output_key = output_key
        self.function_getmtime = datetime.datetime.fromtimestamp(os.path.getmtime(main_file_path))
        self.last_execution = None
        self.env = {}
    
    def set_env(self, data: dict):
        self.env = data
    
    def update_last_execution(self):
        self.last_execution = datetime.datetime.now()
