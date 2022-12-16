rmdir /s /q build
rmdir /s /q dist
rmdir /s /q moethread.egg-info
python setup.py sdist bdist_wheel
twine upload dist/*