import re


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
        Finds backdrop lines and processes them based on
        their commented state and properties.

         Args:
             active_backdrop (string): The selected backdrop URL.
             bg_str (string): The theme-specific CSS text used
             to identify the backdrop line.
        """
        if not active_backdrop:
            return

        with open(self.css_file_path, "r") as file:
            content = file.read()

        # Unified regex pattern for the url lines
        pattern = re.compile(
            # entire line
            r'(?P<full_line>'

            # indent whitespace
            r'(?P<indent>\s*)'

            # capture opening /* (match both uncommented or commented lines)
            r'(?P<comment>/\*)?'

            # property/url declaration
            r'(?P<prop>{}:\s*url\([\'"]?(?P<url>.*?)[\'"]?\)\s*;)'

            # capture end */ (is line commented out?)
            r'(?P<end_comment>\*/)?'

            # trailing comments or whitespace
            r'(?P<trailing>.*)'

            # dynamic insert escaped prop name from given 'bg_str'
            r')'.format(re.escape(bg_str)),
            re.MULTILINE
        )

        # Process regex pattern for each matched backdrop line
        new_lines = []
        for match in pattern.finditer(content):  # find each backdrop link
            groups = match.groupdict()  # extract each group from pattern
            url = groups['url'].strip('\'"')

            if url == active_backdrop:  # uncomment url (indent/prop/trailing)
                new_line = (f"{groups['indent']}{groups['prop']}"
                            f"{groups['trailing']}")
            else:
                new_line = (f"{groups['indent']}/*{groups['prop']}*/"
                            f"{groups['trailing']}")

            new_lines.append((match.start(), match.end(), new_line))

        # Rebuild content only if there are matches found
        if new_lines:
            content_list = list(content)
            for start, end, replace in reversed(new_lines):
                content_list[start:end] = replace

            new_content = "".join(content_list)
            if new_content != content:
                with open(self.css_file_path, "w") as file:
                    file.write(new_content)

    def is_backdrop_commented(self, line):
        """
        Check if the given backdrop line in the file is commented out.

        Args:
            line (string): The line from the CSS file to check.

        Returns:
            (boolean): True if the line is commented out, False otherwise.
        """
        return line.strip().startswith("/*") and line.strip().endswith("*/")
