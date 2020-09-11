i=0
while true; do
    curl --insecure --http1.1 -L -s -X GET -m 3 -I http://172.16.0.2:81/index.html > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR!"
        exit 1
    else
        i=$(expr $i + 1)
        echo "$i"
    fi
done