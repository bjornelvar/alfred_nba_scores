import os

def replace_imports(root_dir, old_import, new_import):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as file:
                    filedata = file.read()
                filedata = filedata.replace(old_import, new_import)
                with open(file_path, 'w') as file:
                    file.write(filedata)

replace_imports('lib/nba_api', 'from nba_api.', 'from lib.nba_api.')