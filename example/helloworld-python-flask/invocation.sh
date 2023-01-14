# curl -H "Host:helloworld-python.default.example.com" http://192.168.122.11:31895/
# curl -H "Host:helloworld-python.default.example.com" http://192.168.122.11:31895/function -d '{"a":"123"}'
# echo ''


curl -H "Host:helloworld-python-flask.default.example.com" http://192.168.122.11/
curl -H "Host:helloworld-python-flask.default.example.com" http://192.168.122.11/function -d '{"a":"123"}'
echo ''
