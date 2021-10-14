# Scripts

The scripts for installing development environment、some command tools、some commonly used softwares, and network proxy configuration.

### install_command_tools.sh

// todo...

### install_software.sh

// todo...

### ios_dev_env.sh

// todo...

### shadowsocks-all.sh

这个是 [@秋水逸冰](https://teddysun.com/)的一键安装脚本

科学上网可以看这篇文章：[科学上网的终极姿势：在 Vultr VPS 上搭建 Shadowsocks](https://zoomyale.com/2016/vultr_and_ss)

安装

```
wget --no-check-certificate -O shadowsocks-all.sh https://raw.githubusercontent.com/teddysun/shadowsocks_install/master/shadowsocks-all.sh

chmod +x shadowsocks-all.sh

./shadowsocks-all.sh 2>&1 | tee shadowsocks-all.log
```

安装完成后，脚本提示如下

```
Congratulations, your_shadowsocks_version install completed!
Your Server IP        :your_server_ip
Your Server Port      :your_server_port
Your Password         :your_password
Your Encryption Method:your_encryption_method

Your QR Code: (For Shadowsocks Windows, OSX, Android and iOS clients)
 ss://your_encryption_method:your_password@your_server_ip:your_server_port
Your QR Code has been saved as a PNG file path:
 your_path.png

Welcome to visit:https://teddysun.com/486.html
Enjoy it!
```

卸载方法
若已安装多个版本，则卸载时也需多次运行（每次卸载一种）

```
./shadowsocks-all.sh uninstall
```

启动脚本
启动脚本后面的参数含义，从左至右依次为：启动，停止，重启，查看状态。

ShadowsocksR 版：
```
/etc/init.d/shadowsocks-r start | stop | restart | status
```
Shadowsocks-Go 版：
```
/etc/init.d/shadowsocks-go start | stop | restart | status
```
Shadowsocks-libev 版：
```
/etc/init.d/shadowsocks-libev start | stop | restart | status
```

各版本默认配置文件

Shadowsocks-Python 版：
```
/etc/shadowsocks-python/config.json
```

ShadowsocksR 版：
```
/etc/shadowsocks-r/config.json
```

Shadowsocks-Go 版：
```
/etc/shadowsocks-go/config.json
```

Shadowsocks-libev 版：
```
/etc/shadowsocks-libev/config.json
```

#### 安装 BBR

```
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh && chmod +x bbr.sh && ./bbr.sh
```

查看BBR是否开启

```
uname -r
lsmod | grep bbr
```

如果输出的内核版本为 4.9 以上版本，且返回值有 `tcp_bbr` 模块的话，说明 bbr 已启动。
