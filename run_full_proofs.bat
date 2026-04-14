@echo off
REM ============================================================================
REM Hyperion SOTA - Complete Proof Runner
REM ============================================================================
REM This runs the FULL SOTA prover and generates complete proofs
REM ============================================================================

echo.
echo ===========================================================================
echo  HYPERION SOTA - THEOREM PROVER vs AXIOMPROVER
echo  "Generating complete, verifiable proofs"
echo ===========================================================================
echo.

REM Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo [1/4] Setting up...
if not exist "hyperion_proofs" (
    mkdir hyperion_proofs
    mkdir hyperion_proofs\lean
    mkdir hyperion_proofs\reports
    mkdir hyperion_proofs\traces
    echo Created output directories
)

echo.
echo [2/4] Choose benchmark mode:
echo.
echo   1. Simulated (fast, no API keys, generates mock proofs)
echo   2. Real (requires Lean 4 + LLM API, actual verification)
echo   3. Putnam 2025 (12 real Putnam problems)
echo.
set /p MODE="Enter choice (1/2/3) [1]: "

if "%MODE%"=="2" (
    echo.
    echo Running REAL SOTA prover...
    echo WARNING: This will use API tokens and take longer!
    echo.
    py run_full_proofs.py --mode real
) else if "%MODE%"=="3" (
    echo.
    echo Running PUTNAM 2025 benchmark...
    echo.
    py benchmark_putnam.py simulated
) else (
    echo.
    echo Running SIMULATED SOTA prover...
    echo.
    py run_full_proofs.py --mode simulated
)

echo.
echo [3/4] Checking generated proofs...
echo.

if exist hyperion_proofs\lean\ (
    echo Generated Lean proofs:
    dir /b hyperion_proofs\lean\*.lean 2>nul | find /c ".lean" >nul
    if not errorlevel 1 (
        for %%f in (hyperion_proofs\lean\*.lean) do (
            echo   [PROOF] %%~nxf
        )
    )
) else (
    echo No proofs generated yet!
)

echo.
if exist hyperion_proofs\reports\summary_report.md (
    echo [4/4] Summary report:
    type hyperion_proofs\reports\summary_report.md | find /c "#" >nul
    echo   See: hyperion_proofs\reports\summary_report.md
) else (
    echo [4/4] No report generated
)

echo.
echo ===========================================================================
echo  RESULTS
echo ===========================================================================
echo.
echo  Proof files:    hyperion_proofs\lean\
echo  Reports:        hyperion_proofs\reports\
echo  Traces:         hyperion_proofs\traces\
echo  Logs:           hyperion_proofs.log
echo.
echo  Next steps:
echo    1. Check hyperion_proofs\lean\*.lean for complete proofs
echo    2. Read hyperion_proofs\reports\summary_report.md for analysis
echo    3. Compare with AxiomProver baseline in reports
echo.
echo  To run with real Lean verification:
echo    py run_full_proofs.py --mode real
echo.
echo ===========================================================================
echo.

pause
