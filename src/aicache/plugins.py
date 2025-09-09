"""
Plugin system for aicache CLI wrappers.
"""

from typing import Dict, Type
from abc import ABC, abstractmethod
import asyncio
import subprocess

class CLIWrapper(ABC):
    """Base class for CLI wrappers."""
    
    @abstractmethod
    def get_cli_name(self) -> str:
        """Return the CLI name this wrapper handles."""
        pass
    
    @abstractmethod
    def parse_arguments(self, args: list) -> tuple[str, dict]:
        """Parse CLI arguments and extract prompt content and context."""
        pass
    
    @abstractmethod
    async def execute_cli(self, args: list) -> tuple[str, int, str]:
        """Execute the actual CLI command and return (stdout, return_code, stderr)."""
        pass
    
    async def _run_cli_command(self, command: str, args: list) -> tuple[str, int, str]:
        """Helper method to run CLI commands."""
        try:
            process = await asyncio.create_subprocess_exec(
                command, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return (
                stdout.decode('utf-8') if stdout else "",
                process.returncode or 0,
                stderr.decode('utf-8') if stderr else ""
            )
        except FileNotFoundError:
            return "", 1, f"Command '{command}' not found"
        except Exception as e:
            return "", 1, f"Error executing command: {e}"


class OpenAIWrapper(CLIWrapper):
    """Wrapper for OpenAI CLI."""
    
    def get_cli_name(self) -> str:
        return "openai"
    
    def parse_arguments(self, args: list) -> tuple[str, dict]:
        """Parse OpenAI CLI arguments."""
        prompt_content = ""
        context = {}
        
        # Look for prompt in various OpenAI CLI patterns
        i = 0
        while i < len(args):
            if args[i] in ['-p', '--prompt'] and i + 1 < len(args):
                prompt_content = args[i + 1]
                i += 2
            elif args[i] in ['-m', '--model'] and i + 1 < len(args):
                context['model'] = args[i + 1]
                i += 2
            else:
                i += 1
        
        return prompt_content, context
    
    async def execute_cli(self, args: list) -> tuple[str, int, str]:
        """Execute OpenAI CLI command."""
        return await self._run_cli_command("openai", args)


class LLMWrapper(CLIWrapper):
    """Wrapper for LLM CLI by Simon Willison."""
    
    def get_cli_name(self) -> str:
        return "llm"
    
    def parse_arguments(self, args: list) -> tuple[str, dict]:
        """Parse LLM CLI arguments."""
        prompt_content = ""
        context = {}
        
        # For llm CLI, the prompt is usually the last argument or after specific flags
        i = 0
        while i < len(args):
            if args[i] in ['-m', '--model'] and i + 1 < len(args):
                context['model'] = args[i + 1]
                i += 2
            elif args[i] in ['-t', '--temperature'] and i + 1 < len(args):
                try:
                    context['temperature'] = float(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif args[i] in ['--max-tokens'] and i + 1 < len(args):
                try:
                    context['max_tokens'] = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif not args[i].startswith('-'):
                # This might be the prompt
                prompt_content = args[i]
                i += 1
            else:
                i += 1
        
        return prompt_content, context
    
    async def execute_cli(self, args: list) -> tuple[str, int, str]:
        """Execute LLM CLI command."""
        return await self._run_cli_command("llm", args)


class GCloudWrapper(CLIWrapper):
    """Wrapper for Google Cloud CLI."""
    
    def get_cli_name(self) -> str:
        return "gcloud"
    
    def parse_arguments(self, args: list) -> tuple[str, dict]:
        """Parse gcloud CLI arguments."""
        # For gcloud, we're mainly interested in AI/ML related commands
        prompt_content = ""
        context = {'cli': 'gcloud'}
        
        # Look for specific AI/ML commands
        if len(args) > 0:
            if 'ai' in args or 'ml' in args:
                prompt_content = ' '.join(args)
                context['service'] = 'ai-ml'
        
        return prompt_content, context
    
    async def execute_cli(self, args: list) -> tuple[str, int, str]:
        """Execute gcloud CLI command."""
        return await self._run_cli_command("gcloud", args)


# Registry of available plugins
REGISTERED_PLUGINS: Dict[str, Type[CLIWrapper]] = {
    'openai': OpenAIWrapper,
    'llm': LLMWrapper,
    'gcloud': GCloudWrapper,
}


def register_plugin(cli_name: str, wrapper_class: Type[CLIWrapper]):
    """Register a new plugin wrapper."""
    REGISTERED_PLUGINS[cli_name] = wrapper_class


def get_plugin(cli_name: str) -> CLIWrapper:
    """Get a plugin wrapper instance."""
    if cli_name in REGISTERED_PLUGINS:
        return REGISTERED_PLUGINS[cli_name]()
    raise ValueError(f"No plugin registered for CLI: {cli_name}")