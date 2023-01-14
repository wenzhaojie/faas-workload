# 如果添加了 /etc/hosts
# knative host bind
# 192.168.122.11 helloworld-python.default.example.com


echo "测试GET /"
hey -c 50 -m GET \
 -z 30s \
 http://helloworld-python.default.example.com



echo "测试POST /function"
hey -c 50 -m POST \
 -z 30s \
 -d '{"a":"123"}' \
 http://helloworld-python.default.example.com/function