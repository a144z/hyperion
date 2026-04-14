@echo off
REM ============================================================================
REM Push to GitHub - Instructions
REM ============================================================================
REM DO NOT use the exposed key. Generate a new one instead!
REM ============================================================================

echo.
echo ===========================================================================
echo  SECURITY WARNING
echo ===========================================================================
echo.
echo  The SSH key you shared is now COMPROMISED.
echo  You MUST generate a new key before pushing to GitHub.
echo.
echo ===========================================================================
echo  SAFE SETUP INSTRUCTIONS
echo ===========================================================================
echo.
echo  Step 1: Generate NEW SSH key
echo    ssh-keygen -t ed25519 -C "your_email@example.com"
echo.
echo  Step 2: Display your NEW public key
echo    cat ~/.ssh/id_ed25519.pub
echo    (or on Windows: type %%USERPROFILE%%\.ssh\id_ed25519.pub)
echo.
echo  Step 3: Add to GitHub
echo    - Go to: https://github.com/settings/keys
echo    - Click "New SSH key"
echo    - Paste the public key
echo.
echo  Step 4: Test connection
echo    ssh -T git@github.com
echo.
echo  Step 5: Push your code
echo    git remote add origin git@github.com:YOUR_USERNAME/hyperion.git
echo    git push -u origin main
echo.
echo ===========================================================================
echo  QUICK SETUP (after generating new key)
echo ===========================================================================
echo.

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not found!
    pause
    exit /b 1
)

echo Current git status:
git status

echo.
echo Remote repositories:
git remote -v

echo.
echo ===========================================================================
echo  TO PUSH (after setting up SSH key):
echo ===========================================================================
echo.
echo  git add .
echo  git commit -m "Hyperion SOTA - Complete upgrade with MCTS and proof decomposition"
echo  git push -u origin main
echo.
echo ===========================================================================
echo.

pause
