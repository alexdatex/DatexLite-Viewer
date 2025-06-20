@echo off
setlocal enabledelayedexpansion

:: -------------------------------
:: Конфигурация и главный скрипт
:: -------------------------------
:: Чтение номера версии из version.py
for /f "tokens=1,2 delims==" %%i in ('type version.py ^| find "VERSION"') do (
    set version=%%j
)
:: Удаление кавычек и пробелов из версии
set version=%version:"=%
set version=%version: =%

:: Конфигурация сборки
set build_number=%version%
set "app_name=DatexLite-Viewer"
set "icon_file=datex.ico"
set "db_file=datex_lite_clean.db"
set ini_file=datexlite_default.ini
set "version_script=add_version.py"

:: Основной процесс сборки
call :delete_folder "dist"
call :delete_folder "build"
call :delete_file "version_info.txt"
call :delete_file "%app_name%.exe.spec"

call :generate_version

pyinstaller --clean --onedir --windowed --target-arch x86_64 --icon=%icon_file% --version-file=version_info.txt --name %app_name%.exe main.py

call :package_application
call :package_application_with_db
call :delete_folder "build"
call :delete_folder "dist"
call :delete_file "version_info.txt"
call :delete_file "%app_name%.exe.spec"


echo Сборка %app_name% версии %build_number% завершена успешно.
endlocal
goto :EOF

:: -------------------------------
:: Функции (в конце файла)
:: -------------------------------

:delete_folder
    if not exist "%~1" (
        echo Папка %~1 не найдена.
        goto :EOF
    )
    echo Удаление папки %~1...
    rmdir /s /q "%~1"
    if exist "%~1" (
        echo Ошибка: Не удалось удалить папку %~1!
        exit /b 1
    )
    echo Папка %~1 успешно удалена.
goto :EOF

:generate_version
    python "%version_script%" %build_number%
    if errorlevel 1 (
        echo ОШИБКА: Генерация version_info.txt не удалась!
        exit /b 1
    )
    if not exist "version_info.txt" (
        echo ОШИБКА: Файл version_info.txt не создан!
        exit /b 1
    )
goto :EOF

:package_application
    :: Форматирование номера сборки (3 цифры)
    set str_build=00%build_number%
    set str_build=%str_build:~-3%

    call :delete_file "%app_name%_%str_build%.7z"
    :: Архивирование
    cd "dist\%app_name%.exe"
    "c:\Program Files\7-Zip\7z" a -mx9 ..\..\%app_name%_%str_build%.7z *
    cd ..\..
    echo Создан архив: %app_name%_%str_build%.zip
goto :EOF

:package_application_with_db
    :: Форматирование номера сборки (3 цифры)
    set str_build=00%build_number%
    set str_build=%str_build:~-3%

    :: Копирование базы данных
    if not exist "%db_file%" (
        echo ОШИБКА: Файл базы данных %db_file% не найден!
        exit /b 1
    )
    copy "%db_file%" "dist\%app_name%.exe\datex_lite.db" >nul

    call :delete_file "%app_name%_%str_build%_with_db.7z"
    :: Архивирование
    cd "dist\%app_name%.exe"
    "c:\Program Files\7-Zip\7z" a -mx9 ..\..\%app_name%_%str_build%_with_db.7z *
    cd ..\..
    echo Создан архив: %app_name%_%str_build%_with_db.zip
goto :EOF

:delete_file
    if not exist "%~1" (
        echo Файл "%~1" не существует.
        goto :EOF
    )
    del /q "%~1"
    if exist "%~1" (
        echo Ошибка: Не удалось удалить файл "%~1"
        exit /b 1
    )
    echo Файл "%~1" успешно удалён.
goto :EOF