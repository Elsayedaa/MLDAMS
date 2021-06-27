echo Preparing to install dependencies...
python -m venv mldamsenv
"%CD%\mldamsenv\Scripts\python.exe" -m pip install requests openpyxl pandas numpy requests Pillow html-table-parser-python3 selenium --pre gql[all]
cd ..\ && cd MATLAB\R2020b\extern\engines && icacls python /grant \Users:(ma,f) /t && cd python && "%CD%\mldamsenv\Scripts\python.exe" setup.py install
pause