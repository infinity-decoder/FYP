import os

def generate_tree(directory, prefix='', output_file=None):
    """Recursively generates a tree structure of folders and files and saves to a file if specified."""
    entries = sorted(os.listdir(directory))  # Sort to maintain order
    entries = [e for e in entries if not e.startswith('.')]  # Ignore hidden files
    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = index == len(entries) - 1
        connector = '└── ' if is_last else '├── '
        line = prefix + connector + entry
        print(line)
        if output_file:
            output_file.write(line + '\n')
        if os.path.isdir(path):
            extension = '    ' if is_last else '│   '
            generate_tree(path, prefix + extension, output_file)

if __name__ == "__main__":
    root_dir = r"D:\FYP"  # Hardcoded directory path
    root_dir = os.path.abspath(root_dir)  # Convert to absolute path
    output_path = os.path.join(root_dir, "folder_structure.txt")  # Output file path
    
    if not os.path.isdir(root_dir):
        print("Invalid directory path.")
    else:
        print(root_dir)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(root_dir + "\n")
            generate_tree(root_dir, output_file=file)
        print(f"Folder structure saved to {output_path}")
