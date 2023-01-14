echo "测试GET /"
hey -c 5 -m GET \
 -z 10s -q 20 \
 -host "helloworld-python-flask.default.example.com" \
 http://192.168.122.11:31895



echo "测试POST /function"
hey -c 5 -m POST \
 -z 10s -q 20 \
 -host "helloworld-python-flask.default.example.com" \
 -d '{"a":"123"}' \
 http://192.168.122.11:31895/function