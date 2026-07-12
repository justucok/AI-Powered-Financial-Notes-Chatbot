import os
import re

def remove_dark_mode_classes(directory):
    # Match an optional leading space, 'dark:', and the class name
    pattern = re.compile(r'\s*\bdark:[a-zA-Z0-9\-\/:]+\b')
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.vue'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                new_content = pattern.sub('', content)
                
                with open(filepath, 'w') as f:
                    f.write(new_content)

if __name__ == '__main__':
    remove_dark_mode_classes('frontend/src')
