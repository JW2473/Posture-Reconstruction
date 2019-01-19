function swap()
{
    local TMPFILE=tmp.$$
    sudo mv "$1" $TMPFILE
    sudo mv "$2" "$1"
    sudo mv $TMPFILE "$2"
}

swap "/etc/dnsmasq.conf"  "/etc/dnsmasq.conf.save"
swap "/etc/default/hostapd"  "/etc/default/hostapd.save"
swap "/etc/dhcpcd.conf"  "/etc/dhcpcd.conf.save"
#swap "/etc/network/interfaces" "/etc/network/interfaces.save"

variableA=$(systemctl is-active hostapd)
if [ $variableA = "active" ]
then
    echo "Hotspot stopped"
    sudo systemctl stop hostapd
    sudo systemctl stop dnsmasq
else
    echo "Hotspot started"
    sudo systemctl start hostapd
    sudo systemctl start dnsmasq
fi
