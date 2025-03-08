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
        Final robust solution for backdrop management
        """
        if not active_backdrop:
            return

        with open(self.css_file_path, "r") as file:
            content = file.read()

        # Unified regex pattern with named groups
        pattern = re.compile(
            r'(?P<full_line>'
            r'(?P<indent>\s*)'
            r'(?P<comment>/\*)?'
            r'(?P<prop>{}:\s*url\([\'"]?(?P<url>.*?)[\'"]?\)\s*;)'
            r'(?P<end_comment>\*/)?'
            r'(?P<trailing>.*)'
            r')'.format(re.escape(bg_str)),
            re.MULTILINE
        )

        # Process matches and track state
        new_lines = []
        active_found = False

        for match in pattern.finditer(content):
            groups = match.groupdict()
            url = groups['url'].strip('\'"')
            is_commented = bool(groups['comment'])

            # Check if this is the selected backdrop
            if url == active_backdrop:
                if not active_found:
                    # Uncomment and activate
                    new_line = f"{groups['indent']}{groups['prop']}{groups['trailing']}"
                    active_found = True
                else:
                    # Comment duplicate entries
                    new_line = f"{groups['indent']}/*{groups['prop']}*/{groups['trailing']}"
            else:
                # Comment other backdrops
                new_line = f"{groups['indent']}/*{groups['prop']}*/{groups['trailing']}"

            new_lines.append((match.start(), match.end(), new_line))

        # Rebuild content only if we found matches
        if new_lines:
            # Replace in reverse order to preserve offsets
            content_list = list(content)
            for start, end, replacement in reversed(new_lines):
                content_list[start:end] = replacement

            # Write back if changes detected
            new_content = ''.join(content_list)
            if new_content != content:
                with open(self.css_file_path, "w") as file:
                    file.write(new_content)
        else:
            print(f"No backdrop lines found for property: {bg_str}")

    def is_backdrop_commented(self, line):
        """
        Check if the given backdrop line in the file is commented out.

        Args:
            line (string): The line from the CSS file to check.

        Returns:
            (boolean): True if the line is commented out, False otherwise.
        """
        return line.strip().startswith("/*") and line.strip().endswith("*/")
