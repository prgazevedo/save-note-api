import re

def sanitize_filename(title):
    """
    Converts a title to a filename-safe string.
    """
    title = title.strip().lower()
    title = re.sub(r'[^a-zA-Z0-9\-_ ]', '', title)
    title = title.replace(' ', '_')
    return title

def build_yaml_block(data):
    """
    Takes a dictionary of metadata fields and returns a YAML frontmatter block.
    """
    lines = ['---']
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(value)}]")
        elif isinstance(value, str) and '\n' in value:
            lines.append(f"{key}: >")
            lines.extend([f"  {line}" for line in value.split('\n')])
        else:
            lines.append(f"{key}: {value}")
    lines.append('---')
    return '\n'.join(lines)
