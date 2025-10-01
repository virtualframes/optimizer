import os

class PRDrafter:
    def create_patch_pr(self, patch: dict, message: str) -> dict:
        """
        Simulates creating a pull request by applying the patch to the local filesystem.
        """
        print(f"PRDrafter: Creating PR with message: {message}")

        if patch.get("action") == "append_to_file":
            file_path = patch["file_path"]
            content = patch["content"]

            print(f"Applying patch: Appending to {file_path}")

            # Ensure the directory exists if the path includes one
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            with open(file_path, "a") as f:
                f.write(content)

            print("Patch applied successfully.")
        else:
            print("Warning: Unknown patch action.")

        # Returns a mock PR object.
        return {
            "url": "https://github.com/example/repo/pull/123",
            "number": 123,
            "state": "open"
        }