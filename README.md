# 관련된 프로젝트 파일을 한번에 오픈 할 수 있게 도와주는 유틸 프로그램입니다.

- 1. 프로그램 실행 시 루트 프로젝트 폴더 경로를 설정해주어야 합니다.
- 2. 프로젝트 폴더 경로는 config.json 파일에 저장됩니다.
- 3. 프로젝트 오픈 시 프로젝트 폴더 경로에서 git pull 과 npm i 를 실행합니다.


# exe 파일 생성 방법
pyinstaller --onefile --noconsole --icon=app_icon.ico --add-data "app_icon.ico;." --add-data "config.json;." main.py

