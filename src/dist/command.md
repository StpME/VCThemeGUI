# To build distributable with pyinstaller:
## Command:

pyinstaller --onefile --noconsole --name VCTheme.exe main.py
pyinstaller --onefile --noconsole --name VCTheme_test.exe main.py

-  Removes console when launching program.
-  Sets desired program name.
-  Builds main script (main.py) and all dependencies (classes and packages) into one file.

Use releases page on github instead of uploading dist folder.