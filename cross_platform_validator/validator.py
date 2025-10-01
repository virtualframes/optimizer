import os
import stat
import subprocess

class CrossPlatformValidator:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def validate_line_endings(self):
        print("INFO: Checking for non-LF line endings...")
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith((".sh", ".yaml", ".yml", ".conf", ".py", ".md", ".txt")):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "rb") as file:
                            content = file.read()
                            if b"\r\n" in content:
                                print(f"  [WARNING] CRLF line endings found in: {path}")
                    except IOError as e:
                        print(f"  [ERROR] Could not read file {path}: {e}")

    def validate_permissions(self):
        print("INFO: Checking for executable permissions on .sh files...")
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith(".sh"):
                    path = os.path.join(root, f)
                    try:
                        mode = os.stat(path).st_mode
                        if not (mode & stat.S_IXUSR):
                            print(f"  [WARNING] Missing executable permission on: {path}")
                    except OSError as e:
                        print(f"  [ERROR] Could not stat file {path}: {e}")

    def validate_paths(self):
        print("INFO: Checking for hardcoded Windows path separators...")
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith((".sh", ".yaml", ".yml", ".conf")):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", errors="ignore") as file:
                            if "\\" in file.read():
                                print(f"  [WARNING] Windows path separator '\\' found in: {path}")
                    except IOError as e:
                        print(f"  [ERROR] Could not read file {path}: {e}")

    def validate_case_sensitivity(self):
        print("INFO: Checking for potential case-sensitivity issues...")
        for root, _, files in os.walk(self.repo_path):
            lowercase_files = [f.lower() for f in files]
            if len(lowercase_files) != len(set(lowercase_files)):
                seen = set()
                dupes = set()
                for f_lower in lowercase_files:
                    if f_lower in seen:
                        dupes.add(f_lower)
                    else:
                        seen.add(f_lower)
                for d in dupes:
                    colliding_files = [f for f in files if f.lower() == d]
                    print(f"  [WARNING] Potential case-sensitivity collision in '{root}': {colliding_files}")

    def validate_shebangs(self):
        print("INFO: Checking for missing shebangs in .sh files...")
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith(".sh"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", errors="ignore") as file:
                            first_line = file.readline()
                            if not first_line.startswith("#!"):
                                print(f"  [WARNING] Missing shebang in: {path}")
                    except IOError as e:
                        print(f"  [ERROR] Could not read file {path}: {e}")

    def validate_symlinks(self):
        print("INFO: Checking for symbolic links...")
        try:
            result = subprocess.run(
                ["find", self.repo_path, "-type", "l"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.stdout.strip():
                print("  [WARNING] Found symbolic links:")
                for line in result.stdout.strip().split('\n'):
                    print(f"    - {line}")
            if result.stderr:
                print(f"  [ERROR] Error checking for symlinks: {result.stderr}")
        except FileNotFoundError:
            print("  [INFO] 'find' command not found. Skipping symlink check.")
        except Exception as e:
            print(f"  [ERROR] An unexpected error occurred during symlink check: {e}")

    def run_all(self):
        print(f"--- Running Cross-Platform Validation on '{self.repo_path}' ---")
        self.validate_line_endings()
        self.validate_permissions()
        self.validate_paths()
        self.validate_case_sensitivity()
        self.validate_shebangs()
        self.validate_symlinks()
        print("--- Validation Complete ---")