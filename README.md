# A Daily Events Digest Mailing Program

This program is inspired by CityU's [daily announcement digest](https://www.cityu.edu.hk/cccu/doc/Access_ePortal_email_2015.pdf) during my exchange.<br>
Emails will be sent automatically everyday, saving your time checking different websites.

### Sample Email
![sample email](https://raw.githubusercontent.com/Rudy1224/nju-daily-digest/master/pics/sample.png)

### Usage

1. Navigate to one folder on your server (assuming it is running on Ubuntu).

2. `git clone` this repository.

3. Copy the example configuration file as `account.ini` and replace the email and server info with your own.

4. Edit the `crontab` file and schedule a new task.<br>
![crontab example](https://raw.githubusercontent.com/Rudy1224/nju-daily-digest/master/pics/crontab.png)

### Requirements
- Python 3.4
- requests

### Task Lists
- [x] Weather and air quality
- [x] Daliy lectures
- [ ] Department lectures
- [ ] University News
- [ ] Announcements by office of academic affairs
- [ ] Exchange program updates
- [ ] BBS hot topics
- [ ] ...

### Contact
lu.huidi`AT`smail`DOT`nju`DOT`edu`DOT`cn
