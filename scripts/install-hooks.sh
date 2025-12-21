#!/bin/bash

# Install git hooks for DevOpsToolbox
# This script creates a pre-push hook that runs tests before allowing a push

HOOKS_DIR=".git/hooks"
PRE_PUSH_HOOK="$HOOKS_DIR/pre-push"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Create pre-push hook
cat > "$PRE_PUSH_HOOK" << 'EOF'
#!/bin/bash

# Pre-push hook to run tests before pushing
# This ensures that only tested code is pushed to the repository

echo "Running tests before push..."

# Run pytest
pytest -v

# Capture the exit code
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Tests failed! Push aborted."
    echo "Fix the failing tests and try again."
    echo ""
    echo "To bypass this check (not recommended), use: git push --no-verify"
    exit 1
fi

echo ""
echo "✅ All tests passed! Proceeding with push..."
echo ""

exit 0
EOF

# Make the hook executable
chmod +x "$PRE_PUSH_HOOK"

echo "✅ Git hooks installed successfully!"
echo ""
echo "The pre-push hook will now run tests before every push."
echo "If tests fail, the push will be rejected."
echo ""
echo "To bypass the hook (not recommended): git push --no-verify"
