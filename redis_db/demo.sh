#!/bin/sh

redis-server --daemonize yes

until redis-cli ping > /dev/null; do
    echo "Waiting for Redis..."
    sleep 2
done

{
redis-cli SET "invitation:TestUser1:3" '{"sender_username": "TestUser3", "board_id": 3, "board_title": "Another regular project"}'
redis-cli SADD "recipient:TestUser1" "invitation:TestUser1:3"
} > /dev/null

redis-cli shutdown

exec redis-server