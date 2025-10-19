import unittest
from unittest.mock import AsyncMock, patch
import sys
import os
import asyncio

# Add the src directory to the python path to import plugins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from aicache.plugins.gemini import GeminiCLIWrapper
from aicache.plugins.qwen import QwenCLIWrapper
from aicache.plugins.claude import ClaudeCLIWrapper

class TestCLIWrappers(unittest.TestCase):

    def setUp(self):
        self.gemini_wrapper = GeminiCLIWrapper()
        self.qwen_wrapper = QwenCLIWrapper()
        self.claude_wrapper = ClaudeCLIWrapper()

    # --- Test GeminiCLIWrapper ---
    def test_gemini_get_cli_name(self):
        self.assertEqual(self.gemini_wrapper.get_cli_name(), "gemini")

    def test_gemini_parse_arguments_simple_prompt(self):
        prompt, context = self.gemini_wrapper.parse_arguments(["some", "command", "my prompt here"])
        self.assertEqual(prompt, "some command my prompt here")
        self.assertIsNone(context["model"])

    def test_gemini_parse_arguments_with_model_long_flag(self):
        prompt, context = self.gemini_wrapper.parse_arguments(["some", "command", "--model", "gemini-pro", "my prompt here"])
        self.assertEqual(prompt, "some command --model gemini-pro my prompt here")
        self.assertEqual(context["model"], "gemini-pro")

    def test_gemini_parse_arguments_with_model_short_flag(self):
        prompt, context = self.gemini_wrapper.parse_arguments(["some", "command", "-m", "gemini-ultra", "my prompt here"])
        self.assertEqual(prompt, "some command -m gemini-ultra my prompt here")
        self.assertEqual(context["model"], "gemini-ultra")

    @patch('shutil.which', return_value='/usr/local/bin/gemini')
    @patch('aicache.plugins.base.CLIWrapper._run_cli_command')
    def test_gemini_execute_cli(self, mock_run_cli_command, mock_shutil_which):
        mock_run_cli_command.return_value = ("stdout", 0, "stderr")
        stdout, return_code, stderr = self.gemini_wrapper.execute_cli(["arg1", "arg2"])
        mock_run_cli_command.assert_called_once_with("/usr/local/bin/gemini", ["arg1", "arg2"])
        self.assertEqual(stdout, "stdout")
        self.assertEqual(return_code, 0)
        self.assertEqual(stderr, "stderr")

    @patch('shutil.which', return_value=None)
    @patch('aicache.plugins.base.CLIWrapper._run_cli_command')
    def test_gemini_execute_cli_not_found(self, mock_run_cli_command, mock_shutil_which):
        stdout, return_code, stderr = self.gemini_wrapper.execute_cli(["arg1"])
        self.assertEqual(stdout, "")
        self.assertEqual(return_code, 1)
        self.assertIn("executable not found", stderr)

    # --- Test QwenCLIWrapper ---
    def test_qwen_get_cli_name(self):
        self.assertEqual(self.qwen_wrapper.get_cli_name(), "qwen")

    def test_qwen_parse_arguments_simple_prompt(self):
        prompt, context = self.qwen_wrapper.parse_arguments(["qwen", "chat", "hello world"])
        self.assertEqual(prompt, "qwen chat hello world")
        self.assertIsNone(context["model"])

    def test_qwen_parse_arguments_with_model_long_flag(self):
        prompt, context = self.qwen_wrapper.parse_arguments(["qwen", "chat", "--model", "qwen-turbo", "how are you"])
        self.assertEqual(prompt, "qwen chat --model qwen-turbo how are you")
        self.assertEqual(context["model"], "qwen-turbo")

    @patch('shutil.which', return_value='/usr/local/bin/qwen')
    @patch('aicache.plugins.base.CLIWrapper._run_cli_command')
    def test_qwen_execute_cli(self, mock_run_cli_command, mock_shutil_which):
        mock_run_cli_command.return_value = ("qwen_stdout", 0, "qwen_stderr")
        stdout, return_code, stderr = self.qwen_wrapper.execute_cli(["argA", "argB"])
        mock_run_cli_command.assert_called_once_with("/usr/local/bin/qwen", ["argA", "argB"])
        self.assertEqual(stdout, "qwen_stdout")
        self.assertEqual(return_code, 0)
        self.assertEqual(stderr, "qwen_stderr")

    @patch('shutil.which', return_value=None)
    @patch('aicache.plugins.base.CLIWrapper._run_cli_command')
    def test_qwen_execute_cli_not_found(self, mock_run_cli_command, mock_shutil_which):
        stdout, return_code, stderr = self.qwen_wrapper.execute_cli(["arg1"])
        self.assertEqual(stdout, "")
        self.assertEqual(return_code, 1)
        self.assertIn("executable not found", stderr)

    # --- Test ClaudeCLIWrapper ---
    def test_claude_get_cli_name(self):
        self.assertEqual(self.claude_wrapper.get_cli_name(), "claude")

    def test_claude_parse_arguments_simple_prompt(self):
        prompt, context = self.claude_wrapper.parse_arguments(["claude", "ask", "what is a haiku?"])
        self.assertEqual(prompt, "claude ask what is a haiku?")
        self.assertIsNone(context["model"])

    def test_claude_parse_arguments_with_model_long_flag(self):
        prompt, context = self.claude_wrapper.parse_arguments(["claude", "ask", "--model", "claude-3-opus", "write a haiku"])
        self.assertEqual(prompt, "claude ask --model claude-3-opus write a haiku")
        self.assertEqual(context["model"], "claude-3-opus")

    @patch('shutil.which', return_value='/usr/local/bin/claude')
    @patch('aicache.plugins.base.CLIWrapper._run_cli_command')
    def test_claude_execute_cli(self, mock_run_cli_command, mock_shutil_which):
        mock_run_cli_command.return_value = ("claude_stdout", 0, "claude_stderr")
        stdout, return_code, stderr = self.claude_wrapper.execute_cli(["query", "--temp", "0.7"])
        mock_run_cli_command.assert_called_once_with("/usr/local/bin/claude", ["query", "--temp", "0.7"])
        self.assertEqual(stdout, "claude_stdout")
        self.assertEqual(return_code, 0)
        self.assertEqual(stderr, "claude_stderr")

    @patch('shutil.which', return_value=None)
    @patch('aicache.plugins.base.CLIWrapper._run_cli_command')
    def test_claude_execute_cli_not_found(self, mock_run_cli_command, mock_shutil_which):
        stdout, return_code, stderr = self.claude_wrapper.execute_cli(["arg1"])
        self.assertEqual(stdout, "")
        self.assertEqual(return_code, 1)
        self.assertIn("executable not found", stderr)

if __name__ == '__main__':
    unittest.main()
