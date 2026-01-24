function usage() {
    echo "usage: $0 [on|off|toggle]"
    exit 1
}

case "$1" in
    "on")
        #curl -X GET "http://plug2.localdomain/rpc/Switch.Set?id=0&on=true"
        ;;
    "off")
        #curl -X GET "http://plug2.localdomain/rpc/Switch.Set?id=0&on=false"
        ;;
    "toggle")
        #curl -X GET http://plug2.localdomain/rpc/Switch.Toggle?id=0
        ;;
    *)
        usage
        ;;
esac


