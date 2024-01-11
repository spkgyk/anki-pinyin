# Create the vendor directory
rm -rf vendor
mkdir -p vendor

# Install dependencies into the vendor directory
pip install --target=vendor -r requirements.txt

# Delete image files and .gitignore files
find vendor -type f \( -name "*.png" -o -name "*.svg" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.gitignore" \) -delete

# Delete .git directories
find vendor -name ".git" -type d -exec rm -rf {} +

# Delete documentation, test files/directories, and other non-essential items
find vendor -type f \( -name "README*" -o -name "CHANGELOG*" -o -name "LICENSE*" -o -name "*.md" -o -name "*.so" \) -delete
find vendor -type d -name "tests" -exec rm -rf {} +
find vendor -type d -name "test" -exec rm -rf {} +
find vendor -type f -name "*.pyc" -delete
find vendor -type d \( -name "examples" -o -name "demos" -o -name "samples" \) -exec rm -rf {} +
find vendor -type f \( -name ".travis.yml" -o -name "setup.py" -o -name "Makefile" -o -name "build.sh" \) -delete
find vendor -type d -path "*.dist-info" -exec rm -rf {} +
rm -rf vendor/_yaml
rm -rf vendor/bin
black . --line-length=140