FROM python:3.8.2

RUN apt update -y

# setup japanese environment
RUN rm /etc/localtime
RUN echo Asia/Tokyo > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt install task-japanese -y

# install google
RUN wget -O ./chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install ./chrome.deb -y
RUN rm ./chrome.deb

# install basic modules
RUN pip install selenium==3.141.0
RUN pip install pandas==1.0.3
RUN pip install slacker==0.14.0
RUN pip install beautifulsoup4==4.9.1
RUN pip install matplotlib==3.2.1
RUN pip install xlrd==1.2.0

# add user. replace `id -u` and `whoami`
#RUN useradd -M -u `id -u` `whoami`
RUN useradd -M -u 1001 kiwi

#setup & start cron
#RUN touch /var/log/cron.log
#CMD cron && tail -f /var/log/cron.log

########################################################
# 1. Run docker with the following option.
#  -v /etc/cron.d:/etc/cron.d
# 2. Better write redirect to logfile in your cronfiles.
#  * * * * * root COMMAND >> /var/log/cron.log
