@echo off
rem setlocal enabledelayedexpansion
:: Чтение номера версии из version.py
for /f "tokens=1,2 delims==" %%i in ('type version.py ^| find "VERSION"') do (
    set version=%%j
)
:: Удаление кавычек и пробелов из версии
set version=%version:"=%
set version=%version: =%
set app_name=DatexLite-Viewer-sources

set str_build=00%version%
set str_build=%str_build:~-3%

:: Проверка наличия 7-Zip
if not exist "c:\Program Files\7-Zip\7z.exe" (
    echo Ошибка: 7-Zip не найден!
    exit /b 1
)

:: Удаление старого архива, если существует
if exist "%app_name%_%str_build%.7z" (
    del "%app_name%_%str_build%.7z"
)

:: Архивирование с исключениями
"c:\Program Files\7-Zip\7z" a -mx9 "%app_name%_%str_build%.7z" * ^
    -xr!".venv" ^
    -xr!".idea" ^
    -xr!".git" ^
    -xr!"__pycache__" ^
    -x!"*.7z" ^
    -x!"*.cmd" ^
    -x!"*.ini" ^
    -x!"logs" ^
    -x!"*.db" ^
    -x!".gitignore"

echo Архив успешно создан: %app_name%_%str_build%.7z
