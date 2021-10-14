#!bin/bash -e

# You can change port and nat
mtproxy_port=8900
nat="10.146.0.2:104.198.122.132"

mtproxy_path="/usr/local/mtproxy"
mtproxy_file="/usr/local/mtproxy/mtproto-proxy"
mtproxy_conf="/usr/local/mtproxy/mtproxy.conf"
mtproxy_secret="/usr/local/mtproxy/proxy-secret"
mtproxy_multi="/usr/local/mtproxy/proxy-multi.conf"
mtproxy_service="/etc/systemd/system/MTProxy.service"

Green_font_prefix="\033[32m" && Red_font_prefix="\033[31m" && Green_background_prefix="\033[42;37m" && Red_background_prefix="\033[41;37m" && Font_color_suffix="\033[0m"
Info="${Green_font_prefix}[信息]${Font_color_suffix}"
Error="${Red_font_prefix}[错误]${Font_color_suffix}"
Tip="${Green_font_prefix}[注意]${Font_color_suffix}"

Check_sys() {
	if [ -f /etc/redhat-release ]; then
		release="centos"
	elif cat /etc/issue | grep -q -E -i "ubuntu"; then
		release="ubuntu"
	fi
}


Check_installed_status(){
	[[ ! -e ${mtproxy_file} ]] && echo -e "${Error} MTProxy 没有安装，请检查 !" && exit 1
}

Download_mtproxy() {
	mkdir '/tmp/mtproxy'
	cd '/tmp/mtproxy'
	git clone https://github.com/TelegramMessenger/MTProxy
	if [ ! -e "MTProxy/" ]; then
		echo "${Error} MTProxy download failed."
		cd '/tmp' && rm -rf '/tmp/mtproxy' && exit 1
	fi

	cd MTProxy
	make
	if [ ! -e "objs/bin/mtproto-proxy" ]; then
		echo "${Error} MTProxy build failed."
		make clean
		cd '/tmp' && rm -rf '/tmp/mtproxy' && exit 1
	fi

	[ ! -e "${mtproxy_path}" ] && mkdir ${mtproxy_path} 
	\cp -f objs/bin/mtproto-proxy ${mtproxy_path}
	chmod +x ${mtproxy_file}
	cd '/tmp' && rm -rf '/tmp/mtproxy'
}

Download_secret() {
	if [ -e "${mtproxy_secret}" ]; then
		rm -rf ${mtproxy_secret}
	fi

	curl -s https://core.telegram.org/getProxySecret -o ${mtproxy_secret}

	if [ ! -e "${mtproxy_secret}" ]; then
		echo "${Error} MTProxy Secret download failed."
	else
		echo "${Info} MTProxy Secret download successfully."
	fi
}

Download_multi_config() {
	if [ -e "${mtproxy_multi}" ]; then
		rm -rf ${mtproxy_multi}
	fi

	curl -s https://core.telegram.org/getProxyConfig -o "${mtproxy_multi}"

	if [ ! -e "${mtproxy_multi}" ]; then
		echo "${Error} MTProxy Multi download failed."
	else
		echo "${Info} MTProxy Multi download successfully."
	fi
}

Set_mtproxy_service() {
	cat > ${mtproxy_service}<<EOF
[Unit]
Description=MTProxy
After=network.target

[Service]
Type=simple
WorkingDirectory=/usr/local/mtproxy
ExecStart=/usr/local/mtproxy/mtproto-proxy -u nobody -p 10000 -H ${mtproxy_port} -S ${mtproxy_passwd} --nat-info ${nat} --aes-pwd proxy-secret proxy-multi.conf -M 1
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
}

Start_mtproxy_service() {
	systemctl daemon-reload
	systemctl restart MTProxy.service
	systemctl status MTProxy.service
	systemctl enable MTProxy.service
}

Get_ip(){
	ip=$(wget -qO- -t1 -T2 ipinfo.io/ip)
	if [[ -z "${ip}" ]]; then
		ip=$(wget -qO- -t1 -T2 api.ip.sb/ip)
		if [[ -z "${ip}" ]]; then
			ip=$(wget -qO- -t1 -T2 members.3322.org/dyndns/getip)
			if [[ -z "${ip}" ]]; then
				ip="VPS_IP"
			fi
		fi
	fi
}

Output_mtproxy() {
	Check_installed_status
	Get_ip
	clear && echo
	echo -e "Mtproto Proxy 用户配置："
	echo -e "————————————————"
	echo -e " IP\t: ${Green_font_prefix}${ip}${Font_color_suffix}"
	echo -e " 端口\t: ${Green_font_prefix}${mtproxy_port}${Font_color_suffix}"
	echo -e " 密匙\t: ${Green_font_prefix}${mtproxy_passwd}${Font_color_suffix}"
	echo
}

Install_mtproxy() {
	# install dependencies
	apt install git curl build-essential libssl-dev zlib1g-dev

	Download_mtproxy
	Download_secret
	Download_multi_config

	Generate_passwd

	# run
	#cd ${mtproxy_path}
	#./mtproto-proxy -u nobody -p 10000 -H ${mtproxy_port} -S ${mtproxy_passwd} --nat-info ${nat} --aes-pwd proxy-secret proxy-multi.conf -M 1

	Output_mtproxy
	Set_mtproxy_service
	Start_mtproxy_service
}

Generate_passwd() {
	mtproxy_passwd=$(head -c 16 /dev/urandom | xxd -ps)
	echo -e "Password: ${Red_background_prefix}${mtproxy_passwd}${Font_color_suffix}"
}

action=$1
case ${action} in
	install)
		Install_mtproxy
		;;
	*)
		echo "Please input correct command"
		;;
esac
