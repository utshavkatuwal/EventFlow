@echo off
cd C:\Projects\EventFlow\backend

:: Start the server in the background
start /wait python -m hypercorn app.main:app --bind 127.0.0.1:8000 --log-level info > server.log 2>&1
timeout /t 5 /nobreak > nul

:: Test login
python -c "
import http.client
import json

# Login
conn = http.client.HTTPConnection('127.0.0.1', 8000)
data = json.dumps({'email': 'admin@eventflow.dev', 'password': 'admin123'}).encode()
conn.request('POST', '/api/v1/auth/login', data, {'Content-Type': 'application/json'})
response = conn.getresponse()
result = json.loads(response.read().decode())
token = result['access_token']
Write-Host \"Token: \" + \$token.Substring(0, 50) + '...'

# Test /users/me
conn = http.client.HTTPConnection('127.0.0.1', 8000)
headers = {'Authorization': 'Bearer ' + \$token, 'User-Agent': 'test-client'}
conn.request('GET', '/api/v1/users/me', headers=headers)
response = conn.getresponse()
Write-Host \"Status: \" + \$response.Status
Write-Host \"Response: \" + \$response.ReadToEnd()
"