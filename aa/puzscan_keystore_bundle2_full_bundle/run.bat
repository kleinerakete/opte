\
    @echo off
    REM Windows launcher - usage: run.bat demo|flask|node [PORT]
    set CMD=%1
    if "%CMD%"=="" set CMD=demo
    set PORT=%2
    if "%PORT%"=="" set PORT=4443

    if /I "%CMD%"=="demo" (
      python server.py %PORT%
      goto :eof
    )
    if /I "%CMD%"=="flask" (
      python app_flask.py %PORT%
      goto :eof
    )
    if /I "%CMD%"=="node" (
      node server_node.js %PORT%
      goto :eof
    )
    echo Unknown command. Use demo, flask or node.
