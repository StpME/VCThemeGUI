import os
import sys
import subprocess
import shutil
import tempfile
# import re


def check_requirements():
    """
    Check if all required modules listed in requirements.txt are installed.
    If not, install them with pip.
    """
    requirements_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "..", "requirements.txt")

    # Ensure requirements.txt exists in src
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found.")
        sys.exit(1)

    # Read the requirements from the file
    with open(requirements_file, "r") as f:
        requirements = f.readlines()

    # Install missing requirements
    for requirement in requirements:
        requirement = requirement.strip()
        if requirement and not requirement.startswith("#"):
            try:  # to import the module
                module_name = requirement.split(">")[0].split("=")[0].strip()
                __import__(module_name)
            except ImportError:
                # If the module is not found, install it
                print(f"Installing missing requirement: {requirement}")
                subprocess.run([sys.executable, "-m", "pip", "install",
                                requirement], check=True)


def check_spec_timestamp_none(spec_file):
    """
    Ensure the spec file has timestamp=None in the EXE section.

    Args:
        spec_file (string): Path to the spec file

    Returns:
        (boolean): True if the file was modified,
                   False if it already had timestamp=None
    """
    with open(spec_file, 'r') as f:
        spec_content = f.read()

    if 'import os' not in spec_content.split('\n')[0:3]:
        spec_content = 'import os\n' + spec_content
        modified = True
    else:
        modified = False

    if 'timestamp=None' not in spec_content:
        # Find the EXE section
        exe_start = spec_content.find('exe = EXE(')
        if exe_start != -1:
            # Find the closing parenthesis
            closing_paren = spec_content.find(')', exe_start)
            if closing_paren != -1:
                # Insert timestamp=None before the closing parenthesis
                modified_content = (
                    spec_content[:closing_paren] +
                    ',\n    timestamp=None' +
                    spec_content[closing_paren:]
                )
                spec_content = modified_content
                modified = True

    # Write the modified content back into spec file if changes detected
    if modified:
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        print("Updated spec file to include timestamp=None")
        return True

    print("Spec file already has timestamp=None, no changes needed")
    return False


def run_pyinstaller(spec_file):
    """
    Run PyInstaller using the spec file.
    Tries standard compilation, then tries
    resolving compression issues, and finally tries
    a fallback to an older pyinstaller if the previous
    approaches fail.

    Args:
        spec_file (string): Path to the spec file.
    """
    # Change wd to the parent directory (src/)
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Clean up existing dist directory
    dist_dir = os.path.join(os.getcwd(), "dist")
    if os.path.exists(dist_dir):
        print(f"Removing existing dist directory: {dist_dir}")
        shutil.rmtree(dist_dir)

    # Ensure the spec file has timestamp=None
    check_spec_timestamp_none(spec_file)

    # Use a shorter temporary directory for the build (250 char cap)
    temp_dir = tempfile.mkdtemp(prefix="VCTheme_")
    os.environ["TEMP"] = temp_dir
    os.environ["TMP"] = temp_dir

    print(f"Using temporary directory: {temp_dir}")
    print(f"Building with spec file: {spec_file}")

    success = False

    # First attempt: Standard build
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", spec_file,
                        "--noconfirm"], check=True)
        print("Successfully built the executable")
        success = True
    except subprocess.CalledProcessError as e:
        print(f"First build attempt failed: {e}")

    # Second attempt: Try --noupx flag (compression issues)
    if not success:
        try:
            print("Trying second build attempt with --noupx flag...")
            subprocess.run([sys.executable, "-m", "PyInstaller", spec_file,
                            "--noconfirm", "--noupx"], check=True)
            print("Successfully built the executable using '--noupx'")
            success = True
        except subprocess.CalledProcessError as e:
            print(f"Second build attempt failed: {e}")

    # Third attempt: Try with PyInstaller 4.10
    if not success:
        try:
            print("Trying third build attempt with PyInstaller version: "
                  "4.10...")
            subprocess.run([sys.executable, "-m", "pip", "install",
                            "pyinstaller==4.10"], check=True)
            subprocess.run([sys.executable, "-m", "PyInstaller", spec_file,
                            "--noconfirm"], check=True)
            print("Successfully built the executable using PyInstaller 4.10")

            # Restore the latest version after building
            subprocess.run([sys.executable, "-m", "pip", "install",
                            "--upgrade", "pyinstaller"], check=True)
            success = True
        except subprocess.CalledProcessError as e:
            print(f"Third build attempt failed: {e}")

    # Clean up the temp directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")

    # If all attempts failed, raise an error
    if not success:
        raise RuntimeError("All build attempts failed. (u_u)")


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

    # Check and install requirements
    check_requirements()

    # Run the build process
    run_pyinstaller(spec_file)

    # Clean up build artifacts
    cleanup_build()

    # Verify the build was successful
    version_file = os.path.join(src_dir, "version.txt")
    with open(version_file, 'r') as f:
        version = f.read().strip()

    exe_path = os.path.join(src_dir, "dist", f"VCTheme_{version}.exe")
    if os.path.exists(exe_path):
        print(f"Build successful! Executable created at: {exe_path}")
    else:
        print("Build completed, "
              "but executable not found at expected location.")


if __name__ == "__main__":
    main()
