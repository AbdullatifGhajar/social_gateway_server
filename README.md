# social_gateway_server

To change the questions you need to reboot the server, do this by copying the questions.json file either to this drive:
scp path_on_your_system kdavis@fb07-neo4j.hpi.uni-potsdam.de:./social_gateway_server/questions.json or by directly editing the file using vim questions.json in this folder

To kill the server, find the current process ID using ´ps -A´  
This prints a large list of processes of which you need to find the one that has gunicorn (name of the server software) as name
kill that process using:
sudo kill xxxxxxx
In which xxxxxxx is the process id (pid) you just found

To reboot the server run this command in the current folder:
/home/kdavis/.local/share/virtualenvs/social_gateway_server-8ajIfuiW/bin/gunicorn -w 1 -b 0.0.0.0:7474 server:app
The response should be similar to this:
[2021-09-05 17:16:07 +0200] [16622] [INFO] Starting gunicorn 19.9.0
[2021-09-05 17:16:07 +0200] [16622] [INFO] Listening at: http://0.0.0.0:7474 (16622)
[2021-09-05 17:16:07 +0200] [16622] [INFO] Using worker: sync
[2021-09-05 17:16:07 +0200] [16625] [INFO] Booting worker with pid: 16625

You can test whether the server is running by visiting https://hpi.de/baudisch/projects/neo4j/api/question?key=hef3TF%5eVg90546bvgFVL%3EZzxskfou;aswperwrsf,c/x
It should present you with one of the questions

To download the answers.csv file use
scp answers.csv path_on_your_system
Which should create a copy of the file on your specified path location

To download the sound files, run the scp command with -r
scp -r /audio path_on_your_system
For all commands here you need to have a VPN connection or be in the HPI network, use EndPointSecurity client from HPI to set this up