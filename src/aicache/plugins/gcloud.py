import shutil
import json
import sys
from pathlib import Path
from .base import CLIWrapper

class GCloudCLIWrapper(CLIWrapper):
    def get_cli_name(self) -> str:
        return "gcloud"

    def parse_arguments(self, args: list) -> tuple[str, dict]:
        json_request_file = None
        for arg in args:
            if arg.startswith("--json-request="):
                json_request_file = arg.split("=", 1)[1]
                break

        if not json_request_file:
            # If no json-request file, we can't cache, so return empty prompt and context
            return "", {}

        try:
            with open(json_request_file, 'r') as f:
                request_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return "", {}

        prompt = request_data.get("instances", [{}])[0].get("prompt", "")
        
        model = None
        for arg in args:
            if arg.startswith("--model="):
                model = arg.split("=", 1)[1]
                break

        context = {"model": model, "request_data": request_data}
        return prompt, context

    def execute_cli(self, args: list) -> tuple[str, int, str]:
        real_gcloud_path = shutil.which("gcloud")
        if not real_gcloud_path:
            return "", 1, "Error: gcloud executable not found."

        return self._run_cli_command(real_gcloud_path, args)
