@echo off  
echo What is doing for is to create a conda environment
echo you should have conda installed before running this script.

set /p choice="Do you want to create a conda environment? (y/n): "
if /i "%choice%"=="y" (
    echo Creating conda environment...
    call conda env create -f environment.yml
    
) else (
    echo Skipping conda environment creation.
)
pause 
    