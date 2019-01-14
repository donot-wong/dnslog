```
 ____  _   _ ____  _
|  _ \| \ | / ___|| |    ___   __ _
| | | |  \| \___ \| |   / _ \ / _` |
| |_| | |\  |___) | |__| (_) | (_| |
|____/|_| \_|____/|_____\___/ \__, |
                              |___/
```

简介
---

本版本是对原四叶草 BugscanTeam 打造的监控 DNS 解析记录和 HTTP 访问记录的工具DNSLog的修改版本。遵循GPL2。
因为原始版本是好几年前开发，一些功能不满足我的需求，因此在源版本基础上进行了重新编码，修改了数据结构、Weblog记录、API等。

安装（Docker）
---

1. 环境准备
Docker环境

2. 获取源代码
```
git clone https://github.com/donot-wong/dnslog.git
``` 

3. 修改配置

```
```

4. 编译镜像
```
cd dnslog
sudo docker build -t dnslog:v1 .
```

5. 启动容器
```
sudo docker run --name dnslog -d -p 53:53/udp -p 127.0.0.1:8082:8000 dnslog:v1
```

6. 配置nginx反向代理
```
server {
	#listen 443 ssl;
	#listen [::]:443 ssl;
	listen 80;
	server_name *.sqvds.cn;

	index index.html index.htm index.nginx-debian.html;
	ssl_certificate ssl/dnslog/1722485_admin.sqvds.cn.pem;
	ssl_certificate_key ssl/dnslog/1722485_admin.sqvds.cn.key;
	ssl_session_timeout 5m;
	ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
	ssl_prefer_server_ciphers on;
	access_log /var/log/nginx/dnslog-access.log;
	error_log /var/log/nginx/dnslog-error.log;
	location / {
		client_max_body_size 100m;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header Host $http_host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_pass http://127.0.0.1:8082;
	}

	location /static {
		alias /home/ubuntu/DNSLog/dnslog/static;
	}
}
```

...未完待续

效果
---

![](./images/1.png)