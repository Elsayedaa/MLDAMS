python -m venv mldamsenv
echo Preparing to install dependencies...
%CD%\mldamsenv\Scripts\python.exe -m pip install requests openpyxl pandas numpy requests Pillow html-table-parser-python3 selenium --pre gql[all]
pause