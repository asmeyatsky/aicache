import re
import shutil
from .base import CLIWrapper

class GeminiCLIWrapper(CLIWrapper):
    def get_cli_name(self) -> str:
        return "gemini"

    def parse_arguments(self, args: list) -> tuple[str, dict]:
        prompt_content = ""
        model = None

        # Assuming the prompt is the last argument, or follows a specific flag
        # For now, let's try to capture the last argument as the prompt
        # This regex might need refinement based on actual gemini CLI usage
        args_str = " ".join(args)
        match = re.search(r'(.*)', args_str) # Very broad, will capture everything
        if match:
            prompt_content = match.group(1)

        # Look for --model or -m flag
        if "--model" in args:
            try:
                model_index = args.index("--model")
                if model_index + 1 < len(args):
                    model = args[model_index + 1]
            except ValueError:
                pass
        elif "-m" in args:
            try:
                model_index = args.index("-m")
                if model_index + 1 < len(args):
                    model = args[model_index + 1]
            except ValueError:
                pass

        context = {'model': model}
        return prompt_content, context

    def execute_cli(self, args: list) -> tuple[str, int, str]:
        # Use shutil.which to find the CLI executable in PATH
        real_cli_path = shutil.which("gemini")
        if real_cli_path is None:
            return "", 1, "Error: 'gemini' executable not found in PATH"
        return self._run_cli_command(real_cli_path, args)

    async def execute_cli_async(self, args: list) -> tuple[str, int, str]:
        # Use shutil.which to find the CLI executable in PATH
        real_cli_path = shutil.which("gemini")
        if real_cli_path is None:
            return "", 1, "Error: 'gemini' executable not found in PATH"
        return await self._run_cli_command_async(real_cli_path, args)
