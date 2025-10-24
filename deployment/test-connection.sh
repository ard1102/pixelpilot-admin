@echo off
echo Testing connection to 192.168.0.100...

echo 1. Testing ping...
ping -n 3 192.168.0.100

echo.
echo 2. Testing SSH connection...
ssh -i "%DEPLOY_SSH_KEY%" -o ConnectTimeout=5 rd@192.168.0.100 "echo SSH connection successful"

echo.
echo 3. Testing port 22 (SSH)...
powershell -command "Test-NetConnection 192.168.0.100 -Port 22"

echo.
echo 4. Testing port 80 (HTTP)...
powershell -command "Test-NetConnection 192.168.0.100 -Port 80"

echo.
echo 5. Testing port 3000 (Coolify)...
powershell -command "Test-NetConnection 192.168.0.100 -Port 3000"

echo.
pause