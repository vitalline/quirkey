# You can use the Python built-in modules to add more functionality.
import re

# Uncomment the following line to enable multiline message input.
# multiline = True


def quirk(text: str) -> str:
    text = re.sub('w', 'uu', text)
    text = re.sub('W', 'UU', text)
    return text
