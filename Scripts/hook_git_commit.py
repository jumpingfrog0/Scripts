import os
import requests
import time
import sys
import re
from urllib.parse import urlencode, quote_plus

# robotKey = '251c8c07-bc75-4869-957b-6e7b1087520c' #测试
# robotKey = '8877a3c6-0e80-4b43-9a74-19f3d0496a21' #迁移版本机器人
robotKey = '664ea1f8-47d6-4c4f-b1b9-d0f9a6999743' #手游语音iOS机器人
#robotKey = 'ea39b4e7-3b3b-4e18-b972-ecb913eb0c0d' #手游业务版本iOS机器人

uids = {'xupengwei' : 'dw_xupengwei', 'zengzhiwei' : 'dw_zengzhiwei',
 'liangyangxing' : 'dw_liangyangxing', 'wangzhenyu' : 'dw_wangzhenyu2',
 'wangzhenyu2' : 'dw_wangzhenyu2', 'wangzhengyu' : 'dw_wangzhenyu2', 
 'wangzhengyu2' : 'dw_wangzhenyu2', 'hehuan' : 'dw_hehuan', 'tubin' : 'dw_tubin',
 'tubing' : 'dw_tubin', 'lichangwen' : 'dw_lichangwen'}

reviewH5Url = 'http://img-syzt.duowan.com/common/codereview.html'
bugH5Url = 'http://project.sysop.duowan.com/browse'
commitH5Url = 'https://git.duowan.com/apps/gamevoice/PIKO-ios/commit'

def postRobot(isMarkdown, content, mentioned_list:[]):
       url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + robotKey
       headers = {"Content-Type": "text/plain"}
       data = {}
       if isMarkdown:
              for userid in mentioned_list:
                     content += "<@%s>"%(userid)
              data = {
                     "msgtype": "markdown",
                     "markdown": {
                            "content": content,
                     }
              }
       else:
              data = {
                     "msgtype": "text",
                     "text": {
                            "content": content,
                            "mentioned_list":mentioned_list
                     }
              } 
       
       requests.post(url, headers=headers, json=data)

def postReview(commitId, commitMsg, currentUser, currentBranch):
       oriReviewer = ''
       matchObj = re.match(r'.*review by.*\[(\S+)\].*', commitMsg, re.S)
       if matchObj:
              oriReviewer = matchObj.group(1)
       reviewer = uids.get(oriReviewer,'')
#        print(reviewer)
       if len(reviewer) == 0 and len(oriReviewer) > 0:
              reviewer = 'dw_' + oriReviewer
       if len(reviewer) == 0:
              return
              
       bugId = ''
       matchObj = re.match(r'.*\[bug id\s+(\S+)\].*', commitMsg, re.S)
       if matchObj:
              bugId = matchObj.group(1)
#        print(bugId)
       hasBugId = len(bugId) > 0

       msg = commitMsg
       if hasBugId:
              matchObj = re.match(r'.*\[bug id.*\](.*)review by.*', commitMsg, re.S)
              if matchObj:
                  msg = matchObj.group(1)
       else:
              matchObj = re.match(r'(.*)review by.*', commitMsg, re.S)
              if matchObj:
                  msg = matchObj.group(1)
       msg = msg.strip()
#        print(msg)

       currentUserID = currentUser
       tempCurrentUser = uids.get(currentUser, '')
       if len(tempCurrentUser) > 0:
           currentUserID = tempCurrentUser
       
       bugIdDesc = '<font color=\"comment\">无</font>'
       if hasBugId:
              bugIdUrl = '%s/%s'%(bugH5Url, bugId)
              bugIdDesc = '<font color=\"comment\">%s</font> [查看](%s)'%(bugId, bugIdUrl)
       currDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
       commitIdUrl = '%s/%s'%(commitH5Url,commitId)
       commitInfo = ">ComitId:<font color=\"comment\">%s</font>\n \
              >BugId:%s\n \
              >描述:<font color=\"comment\">%s</font>\n \
              >时间:<font color=\"comment\">%s</font>\n \
              >分支:<font color=\"comment\">%s</font>"%(commitId[0:8], bugIdDesc, msg, currDate, currentBranch)
       
       payload = {'reviewer':oriReviewer, 'uid':currentUserID, 'commitid':commitId, 'bugId':bugId, 'msg':msg, 'date':currDate, 'robotKey':robotKey}
       encodedContent = urlencode(payload, quote_via=quote_plus)
       reviewedUrl = '%s?%s'%(reviewH5Url,encodedContent)
       reviewedTitle = '[我已完成代码Review](%s)'%(reviewedUrl)

       content = "%s提交了代码 [查看](%s)\n请<@%s>review\n%s\n\n%s"%(currentUser, commitIdUrl, reviewer, commitInfo,reviewedTitle)
       postRobot(True, content, [])

commitId = sys.argv[1]
commitMsg = sys.argv[2]
currentUser = sys.argv[3]
currentBranch = sys.argv[4]
commitCount = sys.argv[5]
if int(commitCount) <= 3:
       postReview(commitId, commitMsg, currentUser, currentBranch)



