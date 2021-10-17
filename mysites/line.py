from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, response
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent,UnfollowEvent,FollowEvent,PostbackEvent,JoinEvent,LeaveEvent, TextSendMessage,TemplateSendMessage,StickerSendMessage,CarouselTemplate,CarouselColumn,URIAction,ImageSendMessage,QuickReply,QuickReplyButton,MessageAction,LocationSendMessage
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import random 
import sqlite3

import os


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
            # print(events)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            profile = line_bot_api.get_profile(event.source.user_id)  
            username=profile.display_name
            if isinstance(event, MessageEvent): #已刪除txt 跟xlsx
                if(event.message.type=="sticker"):
                    sendSticker("requestText",event)
                elif(event.message.type=="location" or event.message.type=="file" or event.message.type=='image' or event.message.type=='video'):
                    print("")
                else:
                    requestText=event.message.text
                    user_id = event.source.user_id #物件
                    user_namelist=[]#所有使用者NAME列表
                    user_idlist=[]#所有使用者ID列表
                    profile = line_bot_api.get_profile(event.source.user_id)  
                    #sql
                    con=sqlite3.connect('db.sqlite3')
                    cur = con.cursor()
                    if os.path.exists("db.sqlite3"):
                            cur.execute('INSERT INTO user (u_id,user_displayname,request) VALUES ("{0}","{1}","{2}")'.format(str(user_id),str(profile.display_name),str(requestText)))
                            print("INSERT complete")
                            for row in list(cur.execute('SELECT DISTINCT u_id,user_displayname FROM user')):#列出所有使用者
                                print("使用者ID",row[0],"使用者名稱",row[1])
                                user_idlist.append(row[0])
                                user_namelist.append(row[1])


                    else:
                            cur.execute('''CREATE TABLE user (user_id text PRIMARY KEY, user_displayname text,)''')
                            print("create succes")
                    con.commit()
                    con.close()
                    #sql
                    nowTime=time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
                    if(user_id==""):
                        break
                    if("@今天天氣 使用方法" == requestText or("@今天天氣" in requestText and "部" in requestText))or("@天氣預報 使用方法" == requestText or("@天氣預報" in requestText and "部" in requestText)):
                        sendQuickreply(requestText,event)
                    elif("@今天天氣" in requestText):
                        sendWeather(requestText,event)
                    elif ("@天氣預報 "in requestText):
                        weatherPredict(requestText,event)
                    elif("@電影" in requestText):
                        nowMovie(requestText,event)
                    elif("@傳送圖片" in requestText):
                        sendImg(requestText,event)
                    elif("@生成圖片" in requestText):
                        randomImg(requestText,event)
                    elif("@聯絡FKT" in requestText):
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="Line ID cxz123499\n"))
                    elif("@調查" in requestText):
                        sendQuickreply(requestText,event)
                    elif("@程式語言" in requestText):
                        storagecode(requestText,event)
                    elif("@關於自己" == requestText or "@關於別人" in requestText):
                        aboutMe(requestText,event,user_idlist,user_namelist)
                    elif("@位置" in requestText):
                        sendLocation(requestText,event)
                    elif("閉嘴" in requestText or "宥融閉嘴" in requestText or "鴻銘"  in requestText):
                        sendImg(requestText,event)
                    elif("語言資料庫" in requestText or "表情包" in requestText):
                        checkSQL(requestText,event)
                    elif("私人訊息" in requestText):
                        sendmsg(requestText,event)
                    elif("@使用說明" in requestText):#輸入一些死豬或猴子的人名
                        msgtext="哈摟!!!"+str(profile.display_name)+"\t功能介紹!!!\n\n\n查看目前上映的電影 \n\tEX: @電影\n天氣預報\n\tEX: 天氣 新竹市\n填寫問卷 \n\tEX: @調查\n小圖片\n\tEX: @傳送圖片 \n查看自己相關資料 \n\t@關於自己"
                        msgtext+="\n\n=============\n!!!新功能(聊天)!!!\n使用方法如下\n\n1.學習功能\n\t讓機器人學習新詞彙\n\tEX:@機器人學 蘋果 很好吃\n\t學習表情包\n\t@機器人學表情 關鍵字 圖片網址\n\n2.查詢當前機器人已經學習的語言\n\t使用方法:\n\t@語言資料庫\n\n3.忘記已經學習過的語言\n\t使用方法:\n\tEX:@機器人忘記 蘋果\n\n\n\t"
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=msgtext))
                    elif("@開機通知" in requestText or"@關機通知" in requestText):
                        if(user_id =='Ub9c1a3d33202f3582d93edb49e63db6b'):
                            sendnotify(requestText, event)
                        else:
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="還想通知? =="+str(profile.display_name)))
                    else:
                        normalRequest(requestText,event)
            elif isinstance(event, JoinEvent):#加入群組
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='歡迎"{0}"加入群組!!!\n'.format(username)))
            elif isinstance(event, LeaveEvent):#離開群組
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='"{0}"離開群組了RIP'.format(username)))
            elif isinstance(event, FollowEvent):#加入好友
        
                with open("userlist.txt","a") as f1:
                    user_id = event.source.user_id
                    f1.write(str(user_id)+"\n")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='"歡迎"{0}"加入好友!!!\n試試看關鍵字 @使用說明 \n來查看我有甚麼功能!? '.format(username)))
            elif isinstance(event, UnfollowEvent):#刪除好友
                
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='"感謝您的使用機器人很高興為您服務使用者:{0}"離開我了掰掰'.format(username)))

            elif isinstance(event, PostbackEvent):#Postback
                requestText=event.message.text
                if("@程式語言" in requestText):
                    storagecode(requestText,event)
        return HttpResponse()

    else:
        return HttpResponseBadRequest()


def normalRequest(requestText,event):
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        user_name=profile.display_name
        if("@機器人學" in requestText):
            learn(requestText,event)
        elif("機器人忘記" in requestText):
            forget(requestText,event)
        elif "范" in requestText or "綱庭" in requestText or "KT" in requestText:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="不不不范綱庭牛逼 "+user_name+"才是死豬 還想偷罵我啊 想不到吧廢物"))
        else:
            
            text=speak(requestText,event)
            if(text == "NULL"):
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="我是鸚鵡會學你說話: "+event.message.text  ))
            else:
                
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text  ))
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤! 資料庫已經有學習過該語言"+str(Exception)))


def sendImg(requestText,event):#貓咪
    try:
        if("鴻銘" in requestText):
               message=ImageSendMessage(
            original_content_url="https://img.onl/3dm1Ug",
            preview_image_url="https://img.onl/3dm1Ug"
            )
        elif("閉嘴" in requestText):
            message=ImageSendMessage(
            original_content_url="https://img.onl/8qUPu",
            preview_image_url="https://img.onl/8qUPu"
            )
        else:
            message=ImageSendMessage(
            original_content_url="https://image.cache.storm.mg/styles/smg-800x533-fp/s3/media/image/2020/01/31/20200131-052418_U17017_M588719_cd2e.jpg?itok=s0SyFjTD",
            preview_image_url="https://image.cache.storm.mg/styles/smg-800x533-fp/s3/media/image/2020/01/31/20200131-052418_U17017_M588719_cd2e.jpg?itok=s0SyFjTD"
            )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤!"))

def randomImg(requestText,event):#picsum
    try:
        
        areaEnter=requestText.split(" ",2)
        inum=random.randint(1,100)
        width=areaEnter[1]
        height=areaEnter[2]
        
        if("模糊" in requestText):
                message=ImageSendMessage(
                original_content_url="https://picsum.photos/"+str(width)+"/"+str(height)+"/?blur",
                preview_image_url="https://picsum.photos"+str(width)+"/"+str(height)+"/?blur"
                )
        elif("灰階" in requestText):
                message=ImageSendMessage(
                original_content_url="https://picsum.photos/"+str(width)+"/"+str(height)+"?grayscale",
                preview_image_url="https://picsum.photos/"+str(width)+"/"+str(height)+"?grayscale"
                )
        else:
                message=ImageSendMessage(
                original_content_url="https://picsum.photos/"+str(width)+"/"+str(height)+"?random="+str(inum),
                preview_image_url="https://picsum.photos/"+str(width)+"/"+str(height)+"?random="+str(inum)
                )
        
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤! 生成圖片使用方法 生成圖片使用方法\n\n一般圖片\n\t@生成圖片 寬 高\n\n灰階圖片\n\t@生成圖片灰階 寬 高\n\n模糊圖片\n\t@生成圖片模糊 寬 高\nEx:@生成圖片 1600 1600"))


def sendSticker(requestText,event):
    try:
        package_list=list()
        package_list.append([446,['1988', '1989', '1990', '1991', '1992']])
        package_list.append([789, ['10855', '10856', '10857', '10858', '10859']])
        package_list.append([1070,['17839', '17840', '17841', '17842', '17843']])
        package_list.append([6136, ['10551376', '10551377', '10551378', '10551379', '10551380']])
        package_list.append([6325, ['10979904', '10979905', '10979906', '10979907', '10979908']])
        package_list.append([6359, ['11069848', '11069849', '11069850', '11069851', '11069852']])
        package_list.append([6362,  ['11087920', '11087921', '11087922', '11087923', '11087924']])
        package_list.append([6370,   ['11088016', '11088017', '11088018', '11088019', '11088020']])
        package_list.append([6632,      ['11825374', '11825375', '11825376', '11825377', '11825378']])
        package_list.append([8515,  ['16581242', '16581243', '16581244', '16581245', '16581246']])
        package_list.append([8522,    ['16581266', '16581267', '16581268', '16581269', '16581270']])
        package_list.append([8525,  ['16581290', '16581291', '16581292', '16581293', '16581294']])
        package_list.append([11537, ['52002734', '52002735', '52002736', '52002737', '52002738']])
        package_list.append([11538,  ['51626494', '51626495', '51626496', '51626497', '51626498']])
        package_list.append([11539,['52114110', '52114111', '52114112', '52114113', '52114114']])
    
        pNum=random.randint(0,len(package_list)-1)
        sNum=random.randint(0,len(package_list[pNum][1])-1)
        # print(package_list[pNum][1])
        # print(pNum,sNum)
      
        messageSticker=StickerSendMessage(
            package_id=str(package_list[pNum][0]),
            sticker_id=package_list[pNum][1][sNum]
        )
        line_bot_api.reply_message(event.reply_token,messageSticker)
    except Exception as e:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤!"+str(e)))

def sendLocation(requestText,event): #Ltitle,Laddress,Llatitude,Llongitude
    try:
        messageLocation=LocationSendMessage(
            title="雲林科技大學",
            address="64002雲林縣斗六市大學路三段123號",
            latitude=23.6959835,
            longitude=120.53410771534355
        )
        line_bot_api.reply_message(event.reply_token,messageLocation)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤!"))






def sendWeather(requestText,event): #天氣
    try:
            url = 'https://news.pchome.com.tw/weather/taiwan'
            response = requests.get(url=url)
            response.encoding
            soup = BeautifulSoup(response.text,"html.parser")
            LocationTaiwan=["基隆市","臺北市","新北市","桃園市","新竹市","新竹縣","苗栗縣","臺中市","彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","臺南市","高雄市","屏東縣","宜蘭縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣"]
            cityEnter=requestText.split(" ",1)
            City = soup.select('.weather-table')
            cityEnter[1] = cityEnter[1].replace('台','臺')
            c1=""
            count=0
            for l in LocationTaiwan:
                count=count+1
                c1=c1+" "+l
                if count % 3 ==0:
                     c1=c1+"\n"
            
            for c in City:
                nationPart=c.find('div',{'class':'nationpart'}).text
                if cityEnter[1] in nationPart:
                    weather_cell=c.find('ul',{'class':'weather-cell'}).find("li")
                    today=weather_cell.find('p',{'class':'day'})
                    icon=weather_cell.find('p',{'class':'icon_box'})
                    temp=weather_cell.find('p',{'class':'temp_s'})
                    
                    T=today.text.split("\t")
                    for i in range(len(T)):
                        if "" in T:
                            T.remove("")
                        if "\n" in T:
                            T.remove("\n")
                    NTT=nationPart.strip()+" "+T[0].strip()+T[(len(T)-1)].strip()+" "+temp.text.strip()
                
            if ((not (cityEnter[1] in  LocationTaiwan))or(cityEnter[1] =="使用方法")):
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="輸入錯誤 查無此縣市\n使用方法:  @今天天氣 臺中市\n本資料庫含有縣市\n\n"+c1))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=NTT))
    except:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤!"))

def nowMovie(requestText,event): #電影
    try:
        url = 'https://movies.yahoo.com.tw/movie_thisweek.html'
        response = requests.get(url=url)
        
        soup = BeautifulSoup(response.text, 'lxml')
        count=0
        sel = soup.find_all("div",{"class":"release_movie_name"})
        s1 =""
        for s in sel:
            count=count+1
            scount=str(count)
            s1=s1+"\n"+scount+": "+(s.find("a",{"class":"gabtn"}).text).strip()
        if (s1.strip().replace("\n",'')==''):
            s1="疫情期間暫無上映電影喔\n在家你我一起防疫看Netflix"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="目前上映的電影\n"+s1))
    except Exception:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤!"+Exception))



def excelfile(request,event): #excelfiletext
    df2 = pd.read_excel('review.xlsx',sheet_name="來自使用者訊息",usecols=["編號", "來源","日期", "訊息"])
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=df2))


def sendnotify(request,event): #sendnotify
    try:
        status=request[1:3]
        group_channel_id1="C800fb3baa653ebbfecf736f167e1ef45"#宿舍群組
        group_channel_id2='C0c2a92d2e687b8d72e74614d36920e81'#工館群組
        user_channel_id1="Ub9c1a3d33202f3582d93edb"#范綱庭
        user_channel_id2='U5c362e1b1d0f0a2f618f3bd444c5b57e'#蘇俊傑
        # line_bot_api.push_message(group_channel_id1,TextSendMessage(text="小叮嚀伺服器開機摟")) #OK
        #宿舍群組 C800fb3baa653ebbfecf736f167e1ef45
        #工館群組 C0c2a92d2e687b8d72e74614d36920e81
        line_bot_api.broadcast(TextSendMessage(text='小叮嚀伺服器'+str(status)+'摟'))
        # line_bot_api.multicast( [user_channel_id1,user_channel_id2], TextSendMessage(text='小叮嚀伺服器開機摟'))#problem
    except Exception as e:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤 錯誤代碼\n'+str(e)))


def sendQuickreply(requestText,event):
    try:
        quest=""
        if("@天氣預報" in requestText):
            quest="@天氣預報"
        elif("@今天天氣" in requestText):
            quest="@今天天氣"
        if("@調查" in requestText):          
            msg=TextSendMessage(
                text="請選擇最喜歡的程式語言",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="Python",text="@程式語言 Python")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="C/C++",text="@程式語言 C/C++")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Java",text="@程式語言 Java")
                            
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="C#",text="@程式語言 C#")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Basic",text="@程式語言 Basic")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="JavaScript",text="@程式語言 JavaScript")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="R",text="@程式語言 R")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="PHP",text="@程式語言 PHP")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Ruby",text="@程式語言 Ruby")
                        ),
                    ]
                )
            )
        elif("@今天天氣 使用方法" in requestText or "@天氣預報 使用方法" in requestText):
             msg=TextSendMessage(
                text="請選擇想查看目前天氣的城市區域",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="北部",text=(str(quest)+" 北部"))
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="中部",text=(str(quest)+" 中部"))
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="南部",text=str(quest)+" 南部")
                            
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="東部及外島",text=str(quest)+" 東部及外島")
                        ),

                                 ]
                )
            )
        elif((str(quest)+" 北部") in requestText):
             msg=TextSendMessage(
                text="請選擇想查看目前天氣的城市",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="基隆市",text=str(quest)+" 基隆市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="臺北市",text=str(quest)+" 臺北市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="新北市",text=str(quest)+" 新北市")
                            
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="桃園市",text=str(quest)+" 桃園市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="新竹市",text=str(quest)+" 新竹市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="新竹縣",text=str(quest)+" 新竹縣")
                        ),
                         QuickReplyButton(
                            action=MessageAction(label="宜蘭縣",text=str(quest)+" 宜蘭縣")
                        ),
                    ]
                )
            )
        elif((str(quest)+" 中部") in requestText):
             msg=TextSendMessage(
                text="請選擇想查看目前天氣的城市",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="苗栗縣",text=str(quest)+" 苗栗縣")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="臺中市",text=str(quest)+" 臺中市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="彰化縣",text=str(quest)+" 彰化縣")
                        ),
                          QuickReplyButton(
                            action=MessageAction(label="南投縣",text=str(quest)+" 南投縣")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="雲林縣",text=str(quest)+" 雲林縣")
                        ),
                    ]
                )
            )
        elif((str(quest)+" 南部") in requestText):
             msg=TextSendMessage(
                text="請選擇想查看目前天氣的城市",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="嘉義市",text=str(quest)+" 嘉義市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="嘉義縣",text=str(quest)+" 嘉義縣")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="臺南市",text=str(quest)+" 臺南市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="高雄市",text=str(quest)+" 高雄市")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="屏東縣",text=str(quest)+" 屏東縣")
                        ),
                    ]
                )
            )
        elif((str(quest)+" 東部及外島") in requestText):
             msg=TextSendMessage(
                text="請選擇想查看目前天氣的城市",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="花蓮縣",text=str(quest)+" 花蓮縣")
                        ),
                          QuickReplyButton(
                            action=MessageAction(label="宜蘭縣",text=str(quest)+" 臺東縣")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="澎湖縣",text=str(quest)+" 澎湖縣")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="金門縣",text=str(quest)+" 金門縣")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="連江縣",text=str(quest)+" 連江縣")
                        ),
                    ]
                )
            )
        line_bot_api.reply_message(event.reply_token, msg)
    except Exception as e:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤!"+str(e)))


def storagecode(requestText,event):
    try:
        profile = line_bot_api.get_profile(event.source.user_id)  
        codeEnter=requestText[6:]
        nowTime=time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
        #sql
        con=sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        if os.path.exists("db.sqlite3"):
                cur.execute('INSERT INTO investigate (User,Date,Program) VALUES ("{0}","{1}","{2}")'.format(str(profile.display_name),nowTime,codeEnter))
                print("INSERT complete")
                        
                for row in list(cur.execute('SELECT * FROM investigate')):
                    print(row)
        else:
                cur.execute('''CREATE TABLE investigate (Number integer PRIMARY KEY, User text, Date text,Program text)''')
                print("create succes")
        con.commit()
        con.close()
        #sql
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="感謝您填寫調查"+str(profile.display_name)))
    except Exception as e:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤!"+str(e)))



cities = ['基隆市','嘉義市','臺北市','嘉義縣','新北市','臺南市','桃園縣','高雄市','新竹市','屏東縣','新竹縣','臺東縣','苗栗縣','花蓮縣','臺中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']
def get(city):
    token = 'CWB-92B895D2-F49F-46A8-9D64-2A9A786F5926'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url)
    print(Data.text)
    Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']
    res = [[] , [] , []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    return res

def weatherPredict(requestText,event):
        message= requestText
        if('@天氣預報' in requestText):
            print("OKOKOKOK")
            city = message[6:]
            city = city.replace('台','臺')
            # 使用者輸入的內容並非符合格式
            if(not (city in cities)):
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="查詢格式為: 天氣 縣市"))
            else:
                # 處理輸出
                res = get(city)

                line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
                    alt_text = city + '未來 36 小時天氣預測',
                    template = CarouselTemplate(
                        columns = [
                            CarouselColumn(
                                thumbnail_image_url = 'https://i.imgur.com/Ex3Opfo.png',
                                title = '{} ~ {}'.format(res[0][0]['startTime'][5:-3],res[0][0]['endTime'][5:-3]),
                                text = '天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(data[0]['parameter']['parameterName'],data[2]['parameter']['parameterName'],data[4]['parameter']['parameterName'],data[1]['parameter']['parameterName']),
                                actions = [
                                    URIAction(
                                        label = '詳細內容',
                                        uri = 'https://www.cwb.gov.tw/V8/C/W/County/index.html'
                                    )
                                ]
                            )for data in res
                        ]
                    )
        ))          

def aboutMe(requestText,event,user_list,user_namelist):#可以做關於別人
    if("自己" in requestText):
        Esource=event.source
        type=Esource.type
        userid=Esource.user_id
        if type =="group":
            groupid=Esource.group_id
        else:
            groupid=""
        Msource=line_bot_api.get_profile(event.source.user_id)
        displayName=Msource.display_name
        language=Msource.language
        pictureUrl=Msource.picture_url

        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="您的資訊如下\n"+"用戶類型\t"+str(type)+"\n使用者ID\t"+str(userid)+"\n當前群組ID\t"+str(groupid)+"\nLine名稱\t"+str(displayName)+"\n使用語言\t"+str(language)+"\n大頭貼連結\t"+str(pictureUrl)) )
    elif("別人" in requestText):
        reply=''
        requestText=requestText.split()
        if (len(requestText)==1):
            reply='本帳戶用戶共計'+str(len(user_list))+'人\n'
            for person_uid in user_list:
                print(person_uid)
                Msource=line_bot_api.get_profile(str(person_uid))
                displayName=Msource.display_name
                language=Msource.language
                pictureUrl=Msource.picture_url
                reply+="\n資訊如下"+"\n使用者ID\t"+str(person_uid)+"\nLine名稱 \t"+str(displayName)+"\n使用語言\t"+str(language)+"\n大頭貼連結\t"+str(pictureUrl)+"\n"
                print(reply)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply ))
        elif(len(requestText)==2):
            for person_uid in user_list:
                Msource=line_bot_api.get_profile(str(person_uid))
                displayName=Msource.display_name
                if(requestText[1]==displayName):
                    language=Msource.language
                    pictureUrl=Msource.picture_url
                    reply+="資訊如下\n"+"\n使用者ID\t"+str(person_uid)+"\nLine名稱\t"+str(displayName)+"\n使用語言\t"+str(language)+"\n大頭貼連結\t"+str(pictureUrl+"\n")
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply ))





def learn(requestText,event):
    userEnter=requestText.split(" ")
    print(userEnter)
    k=userEnter[1]
    v=userEnter[2]
    if(userEnter[0]=="@機器人學表情"):
        con=sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        cur.execute('INSERT INTO image (request,response) VALUES ("{0}","{1}")'.format(k,v))
        print("INSERT Learning complete")
        con.commit()
        con.close()
    if(userEnter[0]=="@機器人學"):
        con=sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        cur.execute('INSERT INTO language (request,response) VALUES ("{0}","{1}")'.format(k,v))
        print("INSERT Learning complete")
        con.commit()
        con.close()
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="已學會"+str(k)+"/"+str(v)))



def speak(requestText,event):
    try:
        con=sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        for response in cur.execute('SELECT * FROM image WHERE request = "{0}"'.format(requestText)):
            print(response)
            if(response[0] in requestText):
                message=ImageSendMessage(
                original_content_url=str(response[1]),
                preview_image_url=str(response[1])
                )
                line_bot_api.reply_message(event.reply_token,message)
        for response in cur.execute('SELECT * FROM language WHERE request LIKE "{0}"'.format(requestText)):
            print(response)
        con.commit()
        con.close()
        return  str(response[1])
    except:
        return  "NULL"

def forget(requestText,event):
    ans=requestText.split(' ')
    print(ans)
    con=sqlite3.connect('db.sqlite3')
    cur = con.cursor()
    cur.execute('DELETE FROM language WHERE request="{0}"'.format(ans[1]) )
    con.commit()
    con.close()
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="I have forgotten: "+str(ans[1])))

def checkSQL(requestText,event):
    con=sqlite3.connect('db.sqlite3')
    cur = con.cursor()
    if("語言" in requestText):
        ans="機器人語言資料庫如下:\n\n"
        count=1
        for response in cur.execute('SELECT * FROM language' ):
                ans+=str(count)+': '+str(response[0])+" "+str(response[1])+"\n"
                count+=1
    if("表情包" in requestText):
        ans="機器人表情包如下:\n\n"
        for response in cur.execute('SELECT * FROM image' ):
                ans+=str(response[0])+" "
    con.commit()
    con.close()
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=str(ans)))

def sendmsg(requestText,event):
    print("Hello World")
#     messages=TextSendMessage(text='Hello World!'),
#     recipient=AudienceRecipient(group_id=5614991017776),
#     filter=Filter(demographic=AgeFilter(gte="age_35", lt="age_40")),
#     limit=Limit(max=10)
# )
