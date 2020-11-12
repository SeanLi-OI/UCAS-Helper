# -*- coding: utf-8 -*-
"""
-----------------Init-----------------------
            Name: humanity.py
            Description:
            Author: Lixiang
            Email: lixiang99410@126.com
            WebSite: https://www.gentlecp.com
            Date: 2020-10-14
-------------Change Logs--------------------


--------------------------------------------
"""
import logging
import re
import time
import requests

from bs4 import BeautifulSoup

from core.login import Loginer


class HlSelector(Loginer):

    def __init__(self, user_info, urls):
        super().__init__(user_info, urls)
        self._logger = logging.getLogger("hl_notify")

    def _get_humanity_lecture(self):
        black_list =[]
        # 获取课程评估url
        try:
            res = self._S.get(url=self._urls['humanity_url']['http'], headers=self.headers, timeout=5)
        except requests.Timeout:
            res = self._S.get(url=self._urls['humanity_url']['https'], headers=self.headers)

        while "你的会话已失效或身份已改变，请重新登录" in res.text:
            self.login()
            try:
                res = self._S.get(url=self._urls['humanity_url']['http'], headers=self.headers, timeout=5)
            except requests.Timeout:
                res = self._S.get(url=self._urls['humanity_url']['https'], headers=self.headers)

        regex = re.compile(r"'(.*?)'")
        hl = BeautifulSoup(res.text, 'lxml')
        
        for alec in hl.find_all("a",string='报名'):
            if 'target' in alec.attrs.keys():
                continue
            plist = regex.findall(alec.attrs['onclick'])
            if plist[0] in black_list:
                self._logger.info("%s in black list."%(plist[0]))
                continue
            pdict = {'lectureId': plist[0],
                    'communicationAddress': plist[1]}
            res = self._S.post(url='http://jwxk.ucas.ac.cn/subject/toSign', data = pdict, headers=self.headers)
            
            if (res.text == 'success'): 
                self._logger.info("select %s success! Time: %s"%(plist[0],plist[1]))

                lecInfo = self._S.get(url="http://jwxk.ucas.ac.cn/subject/%s/humanityView"%(plist[0]), headers=self.headers, timeout=5)
                lecInfo = BeautifulSoup(lecInfo.text, 'lxml')
                lecInfoStr = ['讲座名称','学时','部门','面向对象','开始时间','结束时间','主会场地点','分会场地点','。',]
                lecInfoAll = ""
                for lecInfoi in lecInfo.find_all(text=True):
                    for lecInfoStri in lecInfoStr:
                        if lecInfoi.find(lecInfoStri) != -1:
                            if lecInfoStri == '。':
                                lecInfoAll = lecInfoAll + '讲座介绍：' + lecInfoi + '%0D%0A%0D%0A'
                            else:
                                lecInfoAll = lecInfoAll + lecInfoi + '%0D%0A%0D%0A'
                self._S.post(url=self._urls['ft_url']+"中选时间为%s的人文讲座啦！&desp=%s"%(plist[1],lecInfoAll))

                black_list.append(plist[0])

            else:
                self._logger.info("select %s failed! Error message: %s"%(plist[0],res.text))

    def _select_humanity_lecture(self):
        while True:
            lecture_now = self._get_humanity_lecture()
            time.sleep(1)
            

    def run(self):
        self.login()
        self._select_humanity_lecture()


import settings
if __name__ =='__main__':
    hl_selector = HlSelector(user_info=settings.USER_INFO,
                              urls=settings.URLS)
    hl_selector.run()