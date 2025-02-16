class BackdropManager:
    def __init__(self, css_file_path):
        self.css_file_path = css_file_path

    # Update file with active backdrop
    def update_css_file(self, active_backdrop, bg_str):
        if active_backdrop:
            with open(self.css_file_path, "r") as file:
                lines = file.readlines()

            with open(self.css_file_path, "w") as file:
                for line in lines:
                    if bg_str in line:
                        if active_backdrop in line:
                            if self.is_backdrop_commented(line):
                                file.write(line.replace("/*", "").replace("*/", ""))
                            else:
                                file.write("/*" + line.strip() + "*/\n")
                        elif not self.is_backdrop_commented(line):
                            file.write("/*" + line.strip() + "*/\n")
                        else:
                            file.write(line)
                    else:
                        file.write(line)

    # Check if backdrop is already commented out to prevent appending additional comments
    def is_backdrop_commented(self, line):
        return line.strip().startswith("/*") and line.strip().endswith("*/")
