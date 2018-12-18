function swap()
{
    local TMPFILE=tmp.$$
    mv "$1" $TMPFILE
    mv "$2" "$1"
    mv $TMPFILE "$2"
}

swap "/etc/dnsmasq.conf"  "/etc/dnsmasq.conf.save"
swap "/etc/default/hostapd"  "/etc/default/hostapd.save"
swap "/etc/dhcpcd.conf"  "/etc/dhcpcd.conf.save"

variableA=$(systemctl is-active --quiet hostapd)
if $variableA
then
    echo "Hotspot stopped"
    systemctl stop hostapd
    systemctl stop dnsmasq
else
    echo "Hotspot started"
    systenctl start hostapd
    systemctl start dnsmasq
fi
