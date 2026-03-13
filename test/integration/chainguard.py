"""Validate uv inside the Chainguard distroless Python image.

Unlike the ``chainguard-dev`` image (which includes a shell, pip, and other
tools), the distroless image only ships the Python interpreter. This means
the standard ``check_system_python.py`` script cannot be used because it
relies on ``pip`` and ``which``. Instead, we validate directly with ``uv``
subcommands which don't depend on external tools.
"""

import os
import subprocess
import sys
import tempfile


def main() -> None:
    uv = "/uv"

    with tempfile.TemporaryDirectory() as tmp:
        venv_dir = os.path.join(tmp, ".venv")

        # Create a virtual environment.
        subprocess.run(
            [uv, "venv", venv_dir, "--python", sys.executable],
            check=True,
        )

        python = os.path.join(venv_dir, "bin", "python")
        if not os.path.exists(python):
            raise RuntimeError(f"venv python not found at {python}")

        # Install a package.
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = venv_dir
        subprocess.run(
            [uv, "pip", "install", "iniconfig", "--verbose"],
            env=env,
            check=True,
        )

        # Verify the package is importable.
        subprocess.run(
            [python, "-c", "import iniconfig"],
            check=True,
        )

        # Verify `uv pip show` works.
        subprocess.run(
            [uv, "pip", "show", "iniconfig"],
            env=env,
            check=True,
        )

        # Uninstall the package.
        subprocess.run(
            [uv, "pip", "uninstall", "iniconfig"],
            env=env,
            check=True,
        )

        # Verify the package is no longer importable.
        result = subprocess.run(
            [python, "-c", "import iniconfig"],
            capture_output=True,
        )
        if result.returncode == 0:
            raise RuntimeError("iniconfig should not be importable after uninstall")

    print("All checks passed!")


if __name__ == "__main__":
    main()
