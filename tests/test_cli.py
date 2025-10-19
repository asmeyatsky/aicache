import unittest
import subprocess
import os
import shutil
from pathlib import Path
import sys

class TestCLI(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path.cwd() / "test_project_cli"
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / ".git").mkdir(exist_ok=True)
        os.chdir(self.test_dir)
        # We need to add the src directory to the python path to run the CLI module
        self.cli_path = [sys.executable, "-m", "aicache.cli"]
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
        # Clear the cache before each test
        subprocess.run(self.cli_path + ["clear"], env=self.env, check=True)

    def tearDown(self):
        os.chdir("..")
        shutil.rmtree(self.test_dir)

    def test_cli_inspect(self):
        subprocess.run(self.cli_path + ["set", "prompt_inspect", "response_inspect"], env=self.env)
        import hashlib
        cache_key = hashlib.sha256("prompt_inspect".encode('utf-8')).hexdigest()
        result = subprocess.run(self.cli_path + ["inspect", cache_key], capture_output=True, text=True, env=self.env)
        print(f"Inspect stdout: {result.stdout}")
        print(f"Inspect stderr: {result.stderr}")
        self.assertIn("prompt_inspect", result.stdout)
        self.assertIn("response_inspect", result.stdout)

    def test_cli_list_verbose(self):
        subprocess.run(self.cli_path + ["set", "prompt_list_verbose", "response_list_verbose"], env=self.env)
        result = subprocess.run(self.cli_path + ["list", "--verbose"], capture_output=True, text=True, env=self.env)
        self.assertIn("prompt_list_verbose", result.stdout)

    def test_cli_generate_completions(self):
        result = subprocess.run(self.cli_path + ["generate-completions"], capture_output=True, text=True, env=self.env)
        self.assertIn("_aicache_completions", result.stdout)

    def test_cli_clear_interactive(self):
        subprocess.run(self.cli_path + ["set", "prompt_clear_interactive", "response_clear_interactive"], env=self.env)
        result = subprocess.run(self.cli_path + ["clear", "--interactive"], input="1\n", capture_output=True, text=True, env=self.env)
        self.assertIn("Selected cache entries deleted.", result.stdout)

    def test_cli_prune(self):
        # Create a config file with a small max_size
        config_path = self.test_dir / ".aicache.yaml"
        with open(config_path, "w") as f:
            f.write("intelligent_management:\n  max_size_mb: 0.000001")

        # Add a few entries to exceed max_size
        subprocess.run(self.cli_path + ["set", "prompt1", "response1"], env=self.env, check=True)
        subprocess.run(self.cli_path + ["set", "prompt2", "response2"], env=self.env, check=True)

        # Run prune
        result = subprocess.run(self.cli_path + ["prune"], capture_output=True, text=True, env=self.env)
        self.assertIn("Pruned", result.stdout)

        # Check that the cache is pruned
        result = subprocess.run(self.cli_path + ["stats"], capture_output=True, text=True, env=self.env)
        self.assertIn("Total entries: 1", result.stdout)

    def test_cli_stats(self):
        subprocess.run(self.cli_path + ["set", "prompt_stats_cli", "response_stats_cli"], env=self.env)
        result = subprocess.run(self.cli_path + ["stats"], capture_output=True, text=True, env=self.env)
        self.assertIn("Total entries: 1", result.stdout)

if __name__ == '__main__':
    # We need to add the src directory to the python path to run the tests
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
    unittest.main()
