# 如果添加了 /etc/hosts
# knative host bind
# 192.168.122.11 helloworld-python.default.example.com

curl "http://helloworld-python.default.example.com" 
curl "http://helloworld-python.default.example.com/function"  -d '{"a":"123"}'
echo ''
