.ONESHELL:

.PHONY: start
start:
	@/home/kdavis/.local/share/virtualenvs/social_gateway_server-8ajIfuiW/bin/gunicorn -w 1 -b 0.0.0.0:7474 server:app --reload

.PHONY: stop
stop:
	@for item in $$(pgrep -f gunicorn);	do \
    	kill $$item ; \
	done