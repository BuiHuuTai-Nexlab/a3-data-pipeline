#!/bin/bash
set -e

ZIP_PATH=$(python -c "
import zipfile, os, tempfile
fd, zip_path = tempfile.mkstemp(suffix='.zip')
os.close(fd)
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('utils'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                zf.write(path, path)
print(zip_path)
")
trap 'rm -f "$ZIP_PATH"' EXIT

gsutil -m rsync -r src gs://a3-data-pipeline-code/src
gsutil cp "$ZIP_PATH" gs://a3-data-pipeline-code/utils.zip
echo "Sync done."
