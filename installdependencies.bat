echo Preparing to install dependencies...
cd "%~dp0"
python -m venv mldamsenv
"%~dp0\mldamsenv\Scripts\python.exe" -m pip install requests openpyxl pandas numpy Pillow html-table-parser-python3 selenium pyautogui --pre gql[all]
cd ..\ && cd MATLAB\R2020b\extern\engines && icacls python /grant \Users:(ma,f) /t && cd python && "%~dp0\mldamsenv\Scripts\python.exe" setup.py install
pause