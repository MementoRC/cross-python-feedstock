@echo off
rem cross-python for @CROSS_TARGET_PLATFORM@: build extensions for the target
rem python in %PREFIX% with the build python in %BUILD_PREFIX%.
rem Windows has no _sysconfigdata and crossenv does not support Windows, so
rem the build python is pointed at the target through environment variables
rem and the sitecustomize.py installed in etc\conda\cross-python.
rem No labels or goto here: cmd mis-parses them in LF-only batch files.
if not "%CONDA_BUILD%" == "1" exit /b 0
if "%CONDA_BUILD_STATE%" == "TEST" exit /b 0

set "_CONDA_BACKUP_CROSS_PYTHON_PYTHON=%PYTHON%"
set "_CONDA_BACKUP_CROSS_PYTHON_PATH=%PATH%"
set "_CONDA_BACKUP_CROSS_PYTHON_PYTHONPATH=%PYTHONPATH%"

rem the target python cannot run on the build machine
set "PYTHON=%BUILD_PREFIX%\python.exe"
set "PATH=%BUILD_PREFIX%;%BUILD_PREFIX%\Scripts;%PATH%"

rem read by sitecustomize.py, which makes the build python report the target
set "CROSS_PYTHON_PLATFORM=@CROSS_TARGET_PLATFORM@"
set "CROSS_PYTHON_EXT_SUFFIX=.cp@PY_VER_NODOT@@PY_THREAD@-@PLAT_TAG@.pyd"
set "PYTHONPATH=%BUILD_PREFIX%\etc\conda\cross-python;%PYTHONPATH%"

rem setuptools: target arch, extension suffix, target headers and import libs
set "VSCMD_ARG_TGT_ARCH=arm64"
set "SETUPTOOLS_EXT_SUFFIX=%CROSS_PYTHON_EXT_SUFFIX%"
set "_CROSS_PYTHON_INCLUDE=%PREFIX%\include"
if exist "%PREFIX%\include\python\Python.h" set "_CROSS_PYTHON_INCLUDE=%PREFIX%\include\python"
> "%BUILD_PREFIX%\etc\conda\cross-python\distutils.cfg" (
  echo [build_ext]
  echo plat_name=@CROSS_TARGET_PLATFORM@
  echo include_dirs=%_CROSS_PYTHON_INCLUDE%
  echo library_dirs=%PREFIX%\libs
)
set "DIST_EXTRA_CONFIG=%BUILD_PREFIX%\etc\conda\cross-python\distutils.cfg"
set "_CROSS_PYTHON_INCLUDE="

rem pip: install into the target prefix, not the build python's own
set "PIP_PREFIX=%PREFIX%"

rem pyo3
set "PYO3_CROSS_LIB_DIR=%PREFIX%\libs"
set "PYO3_CROSS_PYTHON_VERSION=@PY_VER@"
set "PYO3_CROSS_PYTHON_IMPLEMENTATION=CPython"
