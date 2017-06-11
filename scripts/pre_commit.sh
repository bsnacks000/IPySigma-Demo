echo "Running pre-commit hook"  
./scripts/run_tests.sh

# $? stores exit value of the last command
if [ $? -ne 0 ]; then  
    echo "Tests must pass before commit... exiting"
    exit 1
fi  