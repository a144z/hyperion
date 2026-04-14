@echo off
REM ============================================================================
REM Hyperion vs AxiomMaths Lab - Complete Benchmark Runner
REM ============================================================================
REM This script runs the full benchmark suite
REM ============================================================================

echo.
echo ===========================================================================
echo  HYPERION THEOREM PROVER - BENCHMARK vs AXIOMMATHS LAB
echo  "Beating AxiomMaths with token efficiency"
echo ===========================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip list | findstr "fastapi" >nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [2/4] Generating real proof set...
python test_real_proofs.py

echo.
echo [3/4] Running benchmark suite...
echo.
echo Choose benchmark mode:
echo   1. Simulated (fast, no API keys needed)
echo   2. Real (requires Lean 4 + LLM API keys)
echo.
set /p MODE="Enter choice (1/2) [1]: "

if "%MODE%"=="2" (
    echo Running REAL benchmark...
    python benchmark.py real
) else (
    echo Running SIMULATED benchmark...
    python benchmark.py simulated
)

echo.
echo [4/4] Generating final report...
echo.

if exist benchmark_results\ (
    echo Results saved in benchmark_results/
    dir /b benchmark_results\
) else (
    echo ERROR: No results generated!
)

echo.
echo ===========================================================================
echo  BENCHMARK COMPLETE
echo ===========================================================================
echo.
echo  Check benchmark_results/ for:
echo    - JSON reports with detailed metrics
echo    - Comparison with AxiomMaths Lab
echo    - Visual charts (if matplotlib available)
echo.
echo  Key question answered:
echo    "Can Hyperion prove theorems with fewer tokens than AxiomMaths?"
echo.
echo ===========================================================================
echo.

pause
