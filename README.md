# Sau Daily Attendence

一个打卡报体温的Python小程序，可以放到vps上用crontab每天定时打卡。

# Feature

 * 打卡失败邮件提醒。
 * 登录后自动保存cookie，尝试每隔30天登录一次更新cookie。
 * 每天只提交一次打卡信息，如果当天打卡成功便不重复提交信息。

# Usage

1. `pip3 install requests`
2. 编辑`config.json`填写智慧沈航的学号和密码，以及需要打卡的信息。`data`中的信息不需要修改。体温可以自动生成。
   如果需要打卡失败邮件提醒，需要配置`mail`中的smtp客户端。
3. `python3 ./main.py -h`
4. `crontab -e` 添加一行 `30 1,2 * * * PATH/TO/main.py >> /PATH/TO/main.log`，意思是在每天凌晨1点30和2点30分提交打卡信息。（可以多设置几个时间，防止因系统崩溃提交失败）

# Others

欢迎提issue。
打卡务必填报真实信息，出现问题请后果自负。
