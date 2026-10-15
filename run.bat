@echo off
chcp 65001 > nul
echo ===================================================
echo [1/3] Проверка и подготовка портативного Python...
echo ===================================================

if not exist "python_portable" (
    echo Скачивание портативного Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip' -OutFile 'python_embed.zip'"
    
    echo Распаковка...
    powershell -Command "Expand-Archive -Path 'python_embed.zip' -DestinationPath 'python_portable'"
    del python_embed.zip

    echo Настройка pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python_portable\get-pip.py'"
    
    :: Разрешаем импорт сторонних библиотек в embed-версии
    echo python311.zip> python_portable\python311._pth
    echo .>> python_portable\python311._pth
    echo import site>> python_portable\python311._pth

    python_portable\python.exe python_portable\get-pip.py --no-warn-script-location
)

echo ===================================================
echo [2/3] Установка необходимых библиотек...
echo ===================================================
python_portable\python.exe -m pip install -r requirements.txt --no-warn-script-location

echo ===================================================
echo [3/3] Запуск Smart Posture Guard...
echo ===================================================
python_portable\python.exe main.py

pause
