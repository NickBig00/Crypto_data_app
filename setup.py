from setuptools import setup

setup(
    name='CryptoPriceApp',
    version='1.0',
    description='A cryptocurrency price tracking application',
    py_modules=['your_script_name'],  # Ersetze 'your_script_name' mit dem Namen deiner Python-Datei ohne .py
    install_requires=[
        'requests',
        'selenium',
        'tkinter',  # tkinter ist in der Regel in Python enthalten, du kannst dies weglassen, falls nicht benötigt
        'concurrent.futures'
    ],
    entry_points={
        'console_scripts': [
            'cryptopriceapp=your_script_name:main',  # Ersetze 'your_script_name' mit dem Namen deiner Python-Datei ohne .py
        ],
    },
)
