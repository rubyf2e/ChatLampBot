#!/bin/sh
envsubst '${PORT_CHATLAMPBOT} ${PORT_CHATLAMPBOT_WEBHOOK}' < /app/supervisord.conf.template > /app/supervisord.conf
exec supervisord -c /app/supervisord.conf