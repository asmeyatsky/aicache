import shutil
import re
import sys
from .base import CLIWrapper

class LLMCLIWrapper(CLIWrapper):
    def get_cli_name(self) -> str:
        return "llm"

    def parse_arguments(self, args: list) -> tuple[str, dict]:
        prompt_args = []
        model = None
        i = 0
        while i < len(args):
            if args[i] in ("-m", "--model"):
                if i + 1 < len(args):
                    model = args[i+1]
                    i += 2
                else:
                    prompt_args.append(args[i])
                    i += 1
            else:
                prompt_args.append(args[i])
                i += 1

        prompt_content = ""
        if not sys.stdin.isatty():
            # If input is from stdin, read it once and store it
            self._stdin_content = sys.stdin.read()
            prompt_content = self._stdin_content
        else:
            prompt_content = " ".join(prompt_args)
            self._stdin_content = None # No stdin content

        context = {"model": model}
        return prompt_content, context

    def execute_cli(self, args: list) -> tuple[str, int, str]:
        real_llm_path = shutil.which("llm")
        if not real_llm_path:
            return "", 1, "Error: llm executable not found."

        return self._run_cli_command(real_llm_path, args, self._stdin_content)
