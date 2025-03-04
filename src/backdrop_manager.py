class BackdropManager:
    """
    Manages the modification of CSS files to update and check active backdrops.
    """

    def __init__(self, css_file_path):
        """
        Initialize the BackdropManager with the path to the CSS file.

        Args:
            css_file_path (string): The path to the CSS file.
        """
        self.css_file_path = css_file_path

    def update_css_file(self, active_backdrop, bg_str):
        """
        Update the CSS file to select or deselect backdrops.

        Args:
            active_backdrop (string): The selected backdrop URL.
            bg_str (string): The theme-specific CSS text used
            to identify backdrop lines.
        """
        if active_backdrop:
            with open(self.css_file_path, "r") as file:
                lines = file.readlines()

            with open(self.css_file_path, "w") as file:
                for line in lines:
                    if bg_str in line and "url(" in line:
                        if active_backdrop in line:
                            if self.is_backdrop_commented(line):
                                # Remove the first /* and the last */
                                uncomm_line = line.replace("/*",
                                                           "", 1).rstrip()
                                # Find the last occurrence of */ and remove it
                                last_comment_end = uncomm_line.rfind("*/")
                                if last_comment_end != -1:
                                    uncomm_line = uncomm_line[
                                        :last_comment_end].rstrip()
                                # Ensure the line ends with a semicolon
                                # ONLY if it doesn't already
                                if not uncomm_line.strip().endswith(";"):
                                    uncomm_line = uncomm_line.rstrip() + ";"
                                file.write(uncomm_line + "\n")
                            else:
                                file.write(line)
                        else:
                            # Comment out the other backdrops
                            if not self.is_backdrop_commented(line):
                                file.write(f"/*{line.strip()}*/\n")
                            else:
                                file.write(line)
                    else:
                        file.write(line)

    def is_backdrop_commented(self, line):
        """
        Check if the given backdrop line in the file is commented out.

        Args:
            line (string): The line from the CSS file to check.

        Returns:
            (boolean): True if the line is commented out, False otherwise.
        """
        return line.strip().startswith("/*") and line.strip().endswith("*/")
