import os
import subprocess
import sys
import shutil
"""
Script to build the executable using PyInstaller.
Run 'python build.py' from the scripts/ directory
to create an executable in a new dist/ directory.
"""


def run_pyinstaller(spec_file):
    """
    Run PyInstaller using the .spec file from src.

    Args:
        spec_file (string): Path to the .spec file.
    """
    try:
        # Change wd to the parent directory (src/)
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Run pyinstaller with the given .spec file
        subprocess.run(["pyinstaller", spec_file], check=True)
        print(f"Successfully built the executable using {spec_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error building the executable: {e}")
        sys.exit(1)


def cleanup_build():
    """
    Clean up unnecessary build artifacts so only exe is kept.
    """
    try:
        # Remove the build dir
        if os.path.exists("build"):
            shutil.rmtree("build")
            print("Cleaned up build directory.")

    except Exception as e:
        print(f"Error during file cleanup: {e}")


def main():
    """
    Main function to build the executable using PyInstaller.
    """
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(scripts_dir)
    spec_file = os.path.join(src_dir, "VCTheme.spec")

    # Ensure the .spec file exists
    if not os.path.exists(spec_file):
        print(f"Error: {spec_file} not found.")
        sys.exit(1)

    run_pyinstaller(spec_file)
    cleanup_build()


if __name__ == "__main__":
    main()
