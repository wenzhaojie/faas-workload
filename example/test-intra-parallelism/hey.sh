echo "测试POST /function"
hey -c 50 -m POST \
 -z 30s -q 200 \
 -host "helloworld-python.default.example.com" \
 -d '{"a":"123"}' \
 http://192.168.122.11:31895/function