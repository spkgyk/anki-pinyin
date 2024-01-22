# Create the src/vendor directory
rm -rf src/vendor
mkdir -p src/vendor

# Install dependencies into the src/vendor directory
pip install --target=src/vendor -r requirements.txt

# Delete image files and .gitignore files
find src/vendor -type f \( -name "*.png" -o -name "*.svg" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.gitignore" \) -delete

# Delete .git directories
find src/vendor -name ".git" -type d -exec rm -rf {} +

# Delete documentation, test files/directories, and other non-essential items
find src/vendor -type f \( -name "README*" -o -name "CHANGELOG*" -o -name "LICENSE*" -o -name "*.md" -o -name "*.so" \) -delete
find src/vendor -type d -name "tests" -exec rm -rf {} +
find src/vendor -type d -name "test" -exec rm -rf {} +
find src/vendor -type f -name "*.pyc" -delete
find src/vendor -type d \( -name "examples" -o -name "demos" -o -name "samples" \) -exec rm -rf {} +
find src/vendor -type f \( -name ".travis.yml" -o -name "setup.py" -o -name "Makefile" -o -name "build.sh" \) -delete
find src/vendor -type d -path "*.dist-info" -exec rm -rf {} +
find src/vendor/pypinyin_dict/phrase_pinyin_data -type f ! -name '*cc_cedict*' -exec rm {} \;
rm -rf src/vendor/pypinyin_dict/pinyin_data
rm -rf src/vendor/_yaml
rm -rf src/vendor/bin
black . --line-length=140
find src/vendor -name '*.py' -exec black --line-length=140 {} +
conda env create -f dev_env.yaml -y