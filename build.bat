@echo off
echo *************CLEAN DIRECTORY*************
rmdir /s /q build
rmdir /s /q dist
for /d %%d in (*.egg-info) do (
    echo Deleting %%d
    rmdir /s /q "%%d"
)
echo *************BUILD WHEEL*************
python setup.py sdist bdist_wheel