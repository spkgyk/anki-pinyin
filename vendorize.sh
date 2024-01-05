# Create the vendor directory
mkdir -p tokenizer/vendor

# Install dependencies into the vendor directory
pip install --target=tokenizer/vendor -r requirements.txt

# Delete image files and .gitignore files
find tokenizer/vendor -type f \( -name "*.png" -o -name "*.svg" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.gitignore" \) -delete

# Delete .git directories
find tokenizer/vendor -name ".git" -type d -exec rm -rf {} +

# Delete documentation, test files/directories, and other non-essential items
find tokenizer/vendor -type f \( -name "README*" -o -name "CHANGELOG*" -o -name "LICENSE*" -o -name "*.md" \) -delete
find tokenizer/vendor -type d -name "tests" -exec rm -rf {} +
find tokenizer/vendor -type d -name "test" -exec rm -rf {} +
find tokenizer/vendor -type f -name "*.pyc" -delete
find tokenizer/vendor -type d \( -name "examples" -o -name "demos" -o -name "samples" \) -exec rm -rf {} +
find tokenizer/vendor -type f \( -name ".travis.yml" -o -name "setup.py" -o -name "Makefile" -o -name "build.sh" \) -delete
