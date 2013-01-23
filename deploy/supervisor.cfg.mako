[supervisord]
logfile = %(here)s/logs/supervisor.log
loglevel = info
pidfile = %(here)s/run/supervisord.pid
directory = %(here)s/code

[unix_http_server]
file = %(here)s/run/supervisord.sock
chown = www-data:www-data
chmod = 0770

[supervisorctl]
serverurl = unix:///%(here)s/run/supervisord.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface


[program:p1]
command = %(here)s/env/bin/paster serve  --server-name=web_01_%(process_num)02d %(here)s/code/${env}.ini
process_name = %(program_name)s-web_01_%(process_num)02d
numprocs=1
autostart = true
startretries=10
autorestart=true
startsecs = 5
user = www-data
redirect_stderr = true
stdout_logfile = %(here)s/logs/python_01_%(process_num)02d.log
environment=PYTHONPATH=%(here)s/code/current