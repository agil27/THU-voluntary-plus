import json
import math
import traceback

from django.shortcuts import render, redirect
from django.utils import timezone
from django.shortcuts import HttpResponse
from django.http import JsonResponse

from . import models as showactivity_models
import mysite.models as mysite_models
from .models import Message, MessageReadOrNot, Activity, ActivityPic, ENROLL_STATE_CONST, Membership, checkin
from mysite.views import checkSessionValid, LOGGED_IN_CONST, PERMISSION_CONST, checkUserType
from mysite.models import VOLUNTEER, UserIdentity

from django.db import transaction

import datetime 
from django.utils.timezone import utc
import requests


FAIL_INFO_KEY = "failinfo"

ranking_last_update_time = datetime.datetime.utcnow()+datetime.timedelta(hours=8) # 排行榜上次更新的时间
ranking_top_100_list = []

BAIDU_MAP_AK = "H5LGjLHfy731eaPCZAUKfAnZH6eiql9M"

# 活动状态
ACTIVITY_STATUS_CONST_NOT_STARTED = "未开始"
ACTIVITY_STATUS_CONST_ALREADY_ENDED = "已结束"
ACTIVITY_STATUS_IN_PROGRESS = "进行中"

def sortListByTime(elem):
    if "starttime" in elem.keys():
        delta = datetime.datetime(int(elem["startdate"].split("-")[0]), int(elem["startdate"].split("-")[1]), \
            int(elem["startdate"].split("-")[2]), int(elem["starttime"].split(":")[0]), \
            int(elem["starttime"].split(":")[1])) - datetime.datetime(1900,1,1,0,0)
        seconds = delta.total_seconds()
        return seconds
    return 0

# 发布活动
def post_activity(request): # name, place, date, time, tag, description, amount
    #print(request.COOKIES)
    print("!!!!!!",checkUserType(request))
    if checkUserType(request) in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        name = json.loads(request.body)["name"]
        city = json.loads(request.body)["city"]
        location = json.loads(request.body)["location"]
        totalNum = json.loads(request.body)["totalNum"]
        startDate = json.loads(request.body)["startdate"]
        startTime = json.loads(request.body)["starttime"].split('T')[1][:5]
        endDate = json.loads(request.body)["enddate"]
        endTime = json.loads(request.body)["endtime"].split('T')[1][:5]
        startDateTime = str(datetime.datetime(int(startDate.split('T')[0].split('-')[0]), int(startDate.split('T')[0].split('-')[1]), int(startDate.split('T')[0].split('-')[2]), \
            int(startDate.split('T')[1][:5].split(':')[0]), int(startDate.split('T')[1][:5].split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[0] 
        startDateTime += " "
        startDateTime += ":".join(str(datetime.datetime(1900, 1, 1, int(startTime.split(':')[0]), int(startTime.split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[1].split(":")[:-1])
        endDateTime = str(datetime.datetime(int(endDate.split('T')[0].split('-')[0]), int(endDate.split('T')[0].split('-')[1]), int(endDate.split('T')[0].split('-')[2]), \
            int(endDate.split('T')[1][:5].split(':')[0]), int(endDate.split('T')[1][:5].split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[0]
        endDateTime += " "
        endDateTime += ":".join(str(datetime.datetime(1900, 1, 1, int(endTime.split(':')[0]), int(endTime.split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[1].split(":")[:-1])
        tag = json.loads(request.body)["tag"]
        description = json.loads(request.body)["desc"]

        try:
            organizer = mysite_models.User.objects.select_for_update().get(username = request.user.username)
        except:
            organizer = None
        activity = Activity(ActivityName = name, ActivityCity = city, ActivityLocation = location, ActivityStartDate = startDateTime, \
            ActivityEndDate = endDateTime, Tag = tag, ActivityIntro = description, ActivityTotalAmount = totalNum, \
            ActivityRemain = totalNum, ActivityOrganizer = organizer)
        activity.save()
        print("POST ACTIVITY SUCCESS")
        return HttpResponse("POST ACTIVITY SUCCESS", status=200)
    else:
        return HttpResponse("NOT AUTHENTICATED", status=401)
   

# 编辑活动
def edit_activity(request): # name, place, date, time, tag, description, amount
    # print(request.COOKIES)
    # print(checkUserType(request))
    if checkUserType(request) in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        activity_id = json.loads(request.body)["id"]
        activity = showactivity_models.Activity.objects.select_for_update().get(id = activity_id)
        if activity.ActivityOrganizer != request.user:
            return HttpResponse("Not your activity!", status=401)

        activity.ActivityName = json.loads(request.body)["name"]
        activity.AcitivityCity = json.loads(request.body)["city"]
        activity.ActivityLocation = json.loads(request.body)["location"]
        startDate = json.loads(request.body)["startdate"]
        startTime = json.loads(request.body)["starttime"].split('T')[1][:5]
        endDate = json.loads(request.body)["enddate"]
        endTime = json.loads(request.body)["endtime"].split('T')[1][:5]
        startDateTime = str(datetime.datetime(int(startDate.split('T')[0].split('-')[0]), int(startDate.split('T')[0].split('-')[1]), int(startDate.split('T')[0].split('-')[2]), \
            int(startDate.split('T')[1][:5].split(':')[0]), int(startDate.split('T')[1][:5].split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[0] 
        startDateTime += " "
        startDateTime += ":".join(str(datetime.datetime(1900, 1, 1, int(startTime.split(':')[0]), int(startTime.split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[1].split(":")[:-1])
        endDateTime = str(datetime.datetime(int(endDate.split('T')[0].split('-')[0]), int(endDate.split('T')[0].split('-')[1]), int(endDate.split('T')[0].split('-')[2]), \
            int(endDate.split('T')[1][:5].split(':')[0]), int(endDate.split('T')[1][:5].split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[0]
        endDateTime += " "
        endDateTime += ":".join(str(datetime.datetime(1900, 1, 1, int(endTime.split(':')[0]), int(endTime.split(':')[1])) + datetime.timedelta(hours=8)).split(" ")[1].split(":")[:-1])
        activity.ActivityStartDate = startDateTime
        activity.ActivityEndDate = endDateTime
        activity.Tag = json.loads(request.body)["tag"]
        activity.ActivityIntro = json.loads(request.body)["desc"]

        activity.save()
        print("POST ACTIVITY SUCCESS")
        return HttpResponse("EDIT ACTIVITY SUCCESS", status=200)
    else:
        return HttpResponse("NOT AUTHENTICATED", status=401)

#显示活动列表

def catalog_grid(request):
    #is_login = request.session.get('is_login', None)
    #if is_login:
    #    user = WX_OPENID_TO_THUID.objects.select_for_update().get(pk=request.session.get('THUID'))
    #if not request.session.get('studentID'):
    #    request.session.flush()
    #   return redirect('/login/')
    # user = check_login(request)
    usertype = checkUserType(request)
    if usertype == PERMISSION_CONST['UNAUTHENTICATED']:
        return HttpResponse("You need to login or bind wxID to THUID!", status = 401)

    if usertype in [PERMISSION_CONST['VOLUNTEER'], PERMISSION_CONST['TEACHER']]:
        rtn_list = showactivity_models.Activity.objects.select_for_update().all()
    else:
        rtn_list = showactivity_models.Activity.objects.select_for_update().filter(ActivityOrganizer = request.user)

    rtn_pic = []
    result = []
    #page_str = request.GET.get('page')
    #if page_str is None:
    #    page = 1
    #else:
    #    page = int(page_str)
    for i in range(len(rtn_list)):
        rtn = {}
        #ActivityID = rtn_list[i].ActivityNumber
        rtn["id"] = rtn_list[i].id
        rtn["title"] = rtn_list[i].ActivityName
        rtn["city"] = rtn_list[i].ActivityCity
        rtn["location"] = rtn_list[i].ActivityLocation
        rtn["tag"] = rtn_list[i].Tag
        rtn["startdate"] = rtn_list[i].ActivityStartDate.split(" ")[0]
        rtn["starttime"] = rtn_list[i].ActivityStartDate.split(" ")[1]
        rtn["enddate"] = rtn_list[i].ActivityEndDate.split(" ")[0]
        rtn["endtime"] = rtn_list[i].ActivityEndDate.split(" ")[1]
        rtn["totalAmount"] = rtn_list[i].ActivityTotalAmount
        rtn["remainAmount"] = rtn_list[i].ActivityRemain
        rtn["desc"] = rtn_list[i].ActivityIntro
        currentTime = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
        endDate = rtn["enddate"]
        endTime = rtn["endtime"]
        rtn["finished"] = compareTime(currentTime.year, currentTime.month, currentTime.day, currentTime.hour, \
            currentTime.minute, int(endDate.split("-")[0]), int(endDate.split("-")[1]), int(endDate.split("-")[2]), \
            int(endTime.split(":")[0]), int(endTime.split(":")[1]))
        rtn["status"] = getActivityStatus(rtn_list[i])
        try:

            rtn["organizer"] = UserIdentity.objects.select_for_update().get(user = rtn_list[i].ActivityOrganizer).groupname
        except:
            rtn["organizer"] = "Unable to get"
        #pic_tmp = showactivity_models.ActivityPic.objects.select_for_update().filter(ActivityNumber=ActivityID)
        #rtn_pic.append(pic_tmp[0])
        #rtn["pic"] = pic_tmp[0]
        result.append(rtn)
    #rtn_dic = dict(map(lambda x, y: [x, y], rtn_pic, rtn_listt))
    #return render(request, "showactivity/catalog_grid.html", locals())
    result.sort(reverse=True, key=sortListByTime)
    return JsonResponse({"ActivityList": result}, safe=False)

# 查看活动详细信息

def activity_detail(request):
    if checkUserType(request) == PERMISSION_CONST['UNAUTHENTICATED']:
        return HttpResponse("You need to login or bind wxID to THUID!", status = 401)
    try:
        THUID = checkSessionValid(request)[1]
        if THUID is None:
            return HttpResponse("Failed to get THUID!", status = 401)
        user = VOLUNTEER.objects.select_for_update().get(pk=THUID)
        activity_id = json.loads(request.body)["activity_id"]
        activity = showactivity_models.Activity.objects.select_for_update().get(id=activity_id)
        #pic = showactivity_models.ActivityPic.objects.select_for_update().filter(ActivityId=activity_id
   # '''
   # class Recommend:
   #     def __init__(self, activity, pic):
   #         self.activity = activity
   #         self.pic = pic
   # activity_rtn = Recommend(activity,pic)
   # '''
        rtn = {}
        rtn["id"] = activity.id
        rtn["title"] = activity.ActivityName
        rtn["city"] = activity.ActivityCity
        rtn["location"] = activity.ActivityLocation
        rtn["tag"] = activity.Tag
        rtn["startdate"] = activity.ActivityStartDate.split(" ")[0]
        rtn["starttime"] = activity.ActivityStartDate.split(" ")[1]
        rtn["enddate"] = activity.ActivityEndDate.split(" ")[0]
        rtn["endtime"] = activity.ActivityEndDate.split(" ")[1]
        rtn["totalAmount"] = activity.ActivityTotalAmount
        rtn["remainAmount"] = activity.ActivityRemain
        rtn["desc"] = activity.ActivityIntro
        rtn["status"] = getActivityStatus(activity)
        try:
            rtn["organizer"] = activity.ActivityOrganizer.username
        except:
            rtn["organizer"] = "Unable to get"
        rtn["participants"] = []
        rtn["checked"] = False
        rtn["already_feedback_provided"] = False
        rtn["registered"] = False
        try:
            membership = Membership.objects.select_for_update().get(activity=activity, volunteer=user)
            rtn["registered"] = True
            rtn["already_feedback_provided"] = membership.already_feedback_provided
            try:
                checkin.objects.select_for_update().get(membership = membership)
                rtn["checked"] = True
            except:
                traceback.print_exc()
                pass
        except:
            traceback.print_exc()
            pass

        for m in Membership.objects.select_for_update().filter(activity=activity):
            if m.state == ENROLL_STATE_CONST['ACCEPTED']:
                volunteer = m.volunteer
                info = {
                    "THUID".lower(): volunteer.THUID,
                    "NAME".lower(): volunteer.NAME,
                    "DEPARTMENT".lower(): volunteer.DEPARTMENT,
                    "NICKNAME".lower(): volunteer.NICKNAME,
                    "SIGNATURE".lower(): volunteer.SIGNATURE,
                    "PHONE".lower(): volunteer.PHONE,
                    "VOLUNTEER_TIME".lower(): volunteer.VOLUNTEER_TIME,
                    "EMAIL".lower(): volunteer.EMAIL
                }
                '''
                try:
                    checkin.objects.select_for_update().get(membership = m)
                    info["already_checked"] = True
                except:
                    info["already_checked"] = False
                '''
                rtn["participants"].append(info)

    #Activity_recommend = showactivity_models.Activity.objects.select_for_update().filter(IsOverDeadline=0)
    #Number_set = set()
    #for gr in Activity_recommend:
    #    Number_set.add(gr.ActivityNumber)
    #Activity_recommend_rtn = []
    #for num in Number_set:
    #        ojb = showactivity_models.Activity.objects.select_for_update().get(ActivityNumber=num)
    #        pic = showactivity_models.ActivityPic.objects.select_for_update().filter(ActivityNumber=num)[0]
    #        Activity_recommend_rtn.append(Recommend(ojb, pic))
    #Activity = showactivity_models.Activity.objects.select_for_update().get(ActivityNumber=Activity_Number)
    #Activity_pic_list = showactivity_models.ActivityPic.objects.select_for_update().filter(ActivityNumber=Activity_Number)
    #studentID = request.session['studentID']
    #user = User.objects.select_for_update().get(studentID=studentID)
    #request.session['number'] = Activity.ActivityNumber
    #return render(request, "showactivity/activity_detail_page.html", locals())
        return JsonResponse(rtn)
    except:
        traceback.print_exc()
        return HttpResponse("INVALID ACTIVITY ID", status=404)

# 返回已经打卡的志愿者名单

def get_unallocated_participants(request):
    usertype = checkUserType(request)
    if usertype in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        activity_id = json.loads(request.body)["id"]
        activity = Activity(id=activity_id)
        res = []
        for info in Membership.objects.select_for_update().filter(activity=activity):
            if info.state != ENROLL_STATE_CONST["ACCEPTED"]: # 只返回已报名通过的志愿者
                continue
            if info.alreadyAssignedVolunteerHour: # 只返回尚未分配工时的志愿者
                continue
            volunteer = info.volunteer
            record = {
                "THUID".lower(): volunteer.THUID,
                "NAME".lower(): volunteer.NAME,
                "DEPARTMENT".lower(): volunteer.DEPARTMENT,
                "NICKNAME".lower(): volunteer.NICKNAME,
                "SIGNATURE".lower(): volunteer.SIGNATURE,
                "PHONE".lower(): volunteer.PHONE,
                "VOLUNTEER_TIME".lower(): volunteer.VOLUNTEER_TIME,
                "EMAIL".lower(): volunteer.EMAIL,
                "checked": False
            }
            try:
                checkin_record = checkin.objects.select_for_update().get(membership=info) # 只返回有打卡记录的志愿者
                record["checked"] = True
                record["checkin_record"]={
                    "latitude": checkin_record.latitude,
                    "longitude": checkin_record.longtitude,
                    "address": checkin_record.address,
                    "checkinTime": checkin_record.checkinTime
                }
            except:
                traceback.print_exc()
                pass
            res.append(record)
        return JsonResponse({"list":res}, safe=False)
    else:
        return HttpResponse("NOT TEACHER OR ORGANIZATION!", status=401)

def compareTime(year1, month1, day1, hour1, minute1, year2, month2, day2, hour2, minute2):
    '''
    若(year1, month1, day1, hour1, minute1)<=(year2, month2, day2, hour2, minute2), 返回True，否则返回False
    '''
    if year1!=year2:
        return year1<year2
    if month1!=month2:
        return month1<month2
    if day1!=day2:
        return day1<day2
    if hour1!=hour2:
        return hour1<hour2
    if minute1!=minute2:
        return minute1<minute2
    return True

# 获取活动状态（未开始/进行中/已结束）
def getActivityStatus(activity:Activity):
    utcnow = (datetime.datetime.utcnow()+datetime.timedelta(hours=8)).replace(tzinfo=utc)
    year = utcnow.year
    month = utcnow.month
    day = utcnow.day
    hour = utcnow.hour
    minute = utcnow.minute
    time1 = activity.ActivityStartDate
    time2 = activity.ActivityEndDate
    year1 = int(time1.split(" ")[0].split("-")[0])
    month1 = int(time1.split(" ")[0].split("-")[1])
    day1 = int(time1.split(" ")[0].split("-")[2])
    hour1 = int(time1.split(" ")[1].split(":")[0])
    minute1 = int(time1.split(" ")[1].split(":")[1])
    year2 = int(time2.split(" ")[0].split("-")[0])
    month2 = int(time2.split(" ")[0].split("-")[1])
    day2 = int(time2.split(" ")[0].split("-")[2])
    hour2 = int(time2.split(" ")[1].split(":")[0])
    minute2 = int(time2.split(" ")[1].split(":")[1])
    if not compareTime(year1, month1, day1, hour1, minute1, year, month, day, hour, minute):
        return ACTIVITY_STATUS_CONST_NOT_STARTED
    elif not compareTime(year, month, day, hour, minute, year2, month2, day2, hour2, minute2):
        return ACTIVITY_STATUS_CONST_ALREADY_ENDED
    else:
        return ACTIVITY_STATUS_IN_PROGRESS


# 签到
def checkinApi(request):
    if checkUserType(request) != PERMISSION_CONST['VOLUNTEER']:
        JsonResponse({"success": False, FAIL_INFO_KEY: "Only logged-in volunteer can checkin!"})
    THUID = checkSessionValid(request)[1]
    if THUID is None:
        return JsonResponse({"success": False, FAIL_INFO_KEY: "Fail to get THUID!"})
    jsonBody = json.loads(request.body)
    volunteer = VOLUNTEER.objects.select_for_update().get(THUID=THUID)
    activity = Activity.objects.select_for_update().get(id=jsonBody["id"])
    try:
        membership = Membership.objects.select_for_update().get(volunteer=volunteer, activity=activity)
        checkin.objects.select_for_update().get(membership=membership)
        return HttpResponse({"success": False, FAIL_INFO_KEY: "You have already checked in!"})
    except:
        pass
    compareTimeResult = getActivityStatus(activity)
    if compareTimeResult != ACTIVITY_STATUS_IN_PROGRESS:
        return JsonResponse({"success": False, FAIL_INFO_KEY: compareTimeResult})
    try:
        date = (datetime.datetime.utcnow()+datetime.timedelta(hours=8)).replace(tzinfo=utc)
        utcnow = "{}-{}-{} {}:{}".format(date.year, date.month, date.day, date.hour, date.minute)
        membership = Membership.objects.select_for_update().get(volunteer=volunteer, activity=activity, state=ENROLL_STATE_CONST['ACCEPTED'])
        latitude = jsonBody["latitude"]
        longitude = jsonBody["longitude"]
        try:
            print(jsonBody)
            address = json.loads(requests.get("http://api.map.baidu.com/reverse_geocoding/v3/?ak={}&output=json&coordtype=wgs84ll&location={},{}".format(BAIDU_MAP_AK, latitude, longitude)).text)
            print(address["status"])
            if address["status"] == 0:
                address = address["result"]["formatted_address"]
            else:
                address = "UNKNOWN"
        except:
            traceback.print_exc()
            address = "UNKNOWN"
        checkin(membership=membership, latitude=jsonBody["latitude"], longtitude=jsonBody["longitude"], checkinTime=utcnow, address=address).save()
        return JsonResponse({"success": True})
    except:
        traceback.print_exc()
        return JsonResponse({"success": False, FAIL_INFO_KEY: "You have not been accepted by the activity organizer"})


def search(request):
    if checkUserType(request) == PERMISSION_CONST['UNAUTHENTICATED']:
        return HttpResponse("You need to login or bind wxID to THUID!", status = 401)
    #user = check_login(request)
    keyword = request.GET.get('search')
    rtn_set = set()
    rtn_list = []
    name_key = showactivity_models.Activity.objects.select_for_update().filter(ActivityName__contains=keyword)
    content_key = showactivity_models.Activity.objects.select_for_update().filter(ActivityIntro__contains=keyword)
    organizer_key = showactivity_models.Activity.objects.select_for_update().filter(ActivityOrganizer__contains=keyword)
    #num_key = showactivity_models.Activity.objects.select_for_update().filter(id__contains=keyword)

    #class Activity:
    #    def __init__(self, id,name,date, pic):
    #        self.id = id
    #        self.pic = pic

    for name in name_key:
        rtn_set.add(name)
    for content in content_key:
        rtn_set.add(content)
    for organizer in organizer_key:
        rtn_set.add(organizer)
    #for num in num_key:
        #rtn_set.add(num)
    rtn_list = []
    for rtn_activity in rtn_set:
        rtn = {}
        rtn["id"] = rtn_activity.id
        rtn["title"] = rtn_activity.ActivityName
        rtn["location"] = rtn_activity.ActivityPlace
        rtn["tag"] = rtn_activity.Tag
        rtn["time1"] = rtn_activity.ActivityStartDate
        rtn["time2"] = rtn_activity.ActivityEndDate
        try:
            rtn["organizer"] = rtn_activity.ActivityOrganizer.username
        except:
            rtn["organizer"] = "Unable to get"
        rtn_list.append(rtn)
        #rtn_list.append(Activity(rtn_activity, showactivity_models.ActivityPic.objects.select_for_update().filter(ActivityNumber=rtn_activity.ActivityNumber)[0], rtn_activity.ActivityTime))
    #return render(request, "showactivity/search.html", locals())
    return JsonResponse(rtn_list)

# 获取消息列表

def message_catalog_grid(request):
    
    # user = User.objects.select_for_update().get(pk = request.session.get('THUID'))
    # message = showactivity_models.Message.objects.select_for_update().get(MessageId=messaage_id)
    usertype = checkUserType(request)
    if usertype == PERMISSION_CONST["VOLUNTEER"]:
        THUID = checkSessionValid(request)[1]
        volunteer = VOLUNTEER(THUID = THUID)
        res = []
        for info in MessageReadOrNot.objects.select_for_update().filter(VolunteerID=volunteer):
              msgInfo = {}
              msg = info.MessageID
              msgInfo["id"] = msg.id
              msgInfo["content"] = msg.MessageDetailContent
              msgInfo["title"] = msg.MessageTitle
              msgInfo["time"] = msg.PostTime
              msgInfo["sender"] = msg.ActivityNumber.ActivityOrganizer.username
              msgInfo["read"] = info.ReadOrNot
              res.append(msgInfo)
        return JsonResponse({"messages":res})
    elif usertype in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        activity_id = json.loads(request.body)["activity_id"]
        activity = Activity.objects.select_for_update().get(id=activity_id)
        res = []
        for msg in Message.objects.select_for_update().filter(ActivityNumber=activity):
            msgInfo = {}
            msgInfo["id"] = msg.id
            msgInfo["title"] = msg.MessageTitle
            msgInfo["content"] = msg.MessageDetailContent
            msgInfo['time'] = msg.PostTime
            res.append(msgInfo)
        return JsonResponse({"messages": res}, safe=False)
    else:
        return HttpResponse("NOT AUTHENTICATED", status=401)
'''
# 读消息
def read_message(request):
    if not checkSessionValid(request):
        return HttpResponse("You need to login!", status = 401)
    THUID = getStudentID(request)
    if THUID == False:
        return HttpResponse("Fail to get THUID!", status = 404)
    # message_id = request.POST.get(message_id)
    user = 
    .objects.select_for_update().get(pk = THUID)
    message_id = request.POST.get(message_id)
    message = showactivity_models.Message.objects.select_for_update().get(id=messaage_id)
    message_ReadOrNot = showactivity_models.MessageReadOrNot.objects.select_for_update().get(MessageId=message_id)
    rtn = {}
    rtn["Title"] = message.MessageTitle
    rtn["DetailContent"] = message.MessageDetailContent
    message_ReadOrNot.update(ReadOrNot = 1)
    message_ReadOrNot.save()
    return JsonResponse({"message_detail":rtn})
'''
# 将消息标记为已读

def mark_read(request):
    if checkUserType(request) == PERMISSION_CONST["VOLUNTEER"]:
        THUID = checkSessionValid(request)[1]
        volunteer = VOLUNTEER(THUID=THUID)
        messaage_id = json.loads(request.body)["id"]
        message = Message.objects.select_for_update().get(id=messaage_id)
        info = MessageReadOrNot.objects.select_for_update().get(VolunteerID=volunteer, MessageID=message)
        info.ReadOrNot = True
        info.save()
        return HttpResponse("SUCCESS", status = 200)
    else:
        return HttpResponse("Only volunteer can read the message", status = 401)

# 删除一条消息

def delete_message(request):
    usertype = checkUserType(request)
    if usertype in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        message_id = json.loads(request.body)["id"]
        message = showactivity_models.Message.objects.select_for_update().get(id = message_id)
        activity = message.ActivityNumber
        if activity.ActivityOrganizer != request.user:
            return HttpResponse("Not your message!", status=401)
        message.delete()
        return HttpResponse("SUCCESS", status=200)
    elif usertype == PERMISSION_CONST["VOLUNTEER"]:
        messaage_id = json.loads(request.body)["id"]
        THUID = checkSessionValid(request)[1]
        volunteer = VOLUNTEER(THUID=THUID)
        message = Message(id=messaage_id)
        MessageReadOrNot.objects.select_for_update().get(VolunteerID=volunteer, MessageID=message).delete()
        return HttpResponse("SUCCESS", status=200)
    else:
        return HttpResponse("Failed to delete message", status = 401)

# 报名活动

def register_activity(request):
    FAIL_INFO_KEY = "failinfo"
    if checkUserType(request) != PERMISSION_CONST['VOLUNTEER']:
        return JsonResponse({"success": False, FAIL_INFO_KEY: "Only logged-in volunteer can register activities!"})
    THUID = checkSessionValid(request)[1]
    if THUID is None:
        return JsonResponse({"success": False, FAIL_INFO_KEY: "Fail to get THUID!"})
    activity_id = json.loads(request.body)["id"]

    user = VOLUNTEER.objects.select_for_update().get(pk = THUID)
    activity = Activity.objects.select_for_update().get(id = activity_id)
    for m in Membership.objects.select_for_update().filter(activity=activity):
        if m.volunteer == user:
            return JsonResponse({"success": False, FAIL_INFO_KEY: "No need to register repeatedly"})

    if activity.ActivityRemain == 0:
        return JsonResponse({"success": False, FAIL_INFO_KEY: "No remain amount!"})

    Membership(volunteer=user, activity = activity, state=ENROLL_STATE_CONST["ACCEPTED"]).save()
    activity.ActivityRemain = activity.ActivityRemain - 1
    activity.save()
    return JsonResponse({"success": True})
    

# 取消报名

def cancel_registration(request):
    if checkUserType(request) != PERMISSION_CONST['VOLUNTEER']:
        return JsonResponse({"success": False, FAIL_INFO_KEY: "Only logged-in volunteer can register activities!"})
    THUID = checkSessionValid(request)[1]
    if THUID is None:
        return JsonResponse({"success": False, FAIL_INFO_KEY: "Fail to get THUID!"})
    activity_id = json.loads(request.body)["id"]

    user = VOLUNTEER.objects.select_for_update().get(pk = THUID)
    activity = Activity.objects.select_for_update().get(id = activity_id)

    already_registered = False
    for m in Membership.objects.select_for_update().filter(activity=activity):
        if m.volunteer == user:
            already_registered = True

    if not already_registered:
        return JsonResponse({"success": False, FAIL_INFO_KEY: "You need to register before cancelling it"})

    activity.members.remove(user)
    activity.ActivityRemain = activity.ActivityRemain + 1
    activity.save()
    return JsonResponse({"success": True})

# 发布消息

def post_message(request):
    if checkUserType(request) in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        print(json.loads(request.body))
        activity_id = json.loads(request.body)["activity_id"]
        activity = showactivity_models.Activity.objects.select_for_update().get(id=activity_id)
        if activity.ActivityOrganizer != request.user:
            return HttpResponse("Not your activity", status=401)
        title = json.loads(request.body)["title"]
        content = json.loads(request.body)["content"]
        date = (datetime.datetime.utcnow()+datetime.timedelta(hours=8)).replace(tzinfo=utc)
        date = "{}-{}-{}".format(date.year, date.month, date.day)
        message = Message(MessageTitle = title, MessageDetailContent = content,ActivityNumber = activity, PostTime = date)
        message.save()
        volunteers = activity.members
        for volunteer in volunteers.all():
            membership = Membership.objects.select_for_update().get(volunteer = volunteer, activity = activity)
            if membership.state == ENROLL_STATE_CONST['ACCEPTED']:
                message.volunteers.add(volunteer)
        message.save()
        return HttpResponse("Post messages successful", status = 200)
    else:
        return HttpResponse("You have no access", status = 401)

# 编辑消息

def edit_message(request):
    if checkUserType(request) in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        message_id = json.loads(request.body)["id"]
        message = showactivity_models.Message.objects.select_for_update().get(id = message_id)
        activity = message.ActivityNumber
        if activity.ActivityOrganizer != request.user:
            return HttpResponse("Not your message!", status=401)
        message.MessageTitle = json.loads(request.body)["title"]
        message.MessageDetailContent = json.loads(request.body)["content"]
        date = (datetime.datetime.utcnow()+datetime.timedelta(hours=8)).replace(tzinfo=utc)
        date = "{}-{}-{}".format(date.year, date.month, date.day)
        message.PostTime = date
        message.save()
        return HttpResponse("SUCCESS", status=200)
    else:
        return HttpResponse("Not authenticated!", status=401)    

# 获取用户参加活动的历史

def get_volunteer_history(request):
    usertype = checkUserType(request)
    if usertype == PERMISSION_CONST['VOLUNTEER']:
        THUID = checkSessionValid(request)[1]
        volunteer = VOLUNTEER(THUID=THUID)
        resList = []
        for record in Membership.objects.select_for_update().filter(volunteer=volunteer):
            activity = record.activity
            rtn = {}
            rtn["id"] = activity.id
            rtn["title"] = activity.ActivityName
            rtn["city"] = activity.ActivityCity
            rtn["location"] = activity.ActivityLocation
            rtn["tag"] = activity.Tag
            rtn["startdate"] = activity.ActivityStartDate.split(" ")[0]
            rtn["starttime"] = activity.ActivityStartDate.split(" ")[1]
            rtn["enddate"] = activity.ActivityEndDate.split(" ")[0]
            rtn["endtime"] = activity.ActivityEndDate.split(" ")[1]
            rtn["totalAmount"] = activity.ActivityTotalAmount
            rtn["remainAmount"] = activity.ActivityRemain
            rtn["desc"] = activity.ActivityIntro
            try:
                rtn["organizer"] = activity.ActivityOrganizer.username
            except:
                rtn["organizer"] = "Unable to get"
            state = record.state
            rtn["state"] = 'UNCENSORED'
            for state_key in ['ACCEPTED', 'UNCENSORED', 'REJECTED']:
                if state == ENROLL_STATE_CONST[state_key]:
                    rtn["state"] = state_key
                    break
            resList.append(rtn)
        return JsonResponse({"history": resList}, safe=False)
    else:
        return HttpResponse("NOT A VOLUNTEER!", status=401)

# 获取排行榜

def get_ranking(request):
    global ranking_last_update_time, ranking_top_100_list
    usertype = checkUserType(request)
    if usertype == PERMISSION_CONST["UNAUTHENTICATED"]:
        return HttpResponse("UNAUTHENTICATED", status=401)
    outdated =  (datetime.datetime.utcnow()+datetime.timedelta(hours=8)-ranking_last_update_time).total_seconds() > (5*60) # 每5min更新一次排行榜
    if outdated or (len(ranking_top_100_list) == 0):
        new_top_100_list = []
        order = 1
        for volunteer in VOLUNTEER.objects.select_for_update().all().order_by('-VOLUNTEER_TIME'):
            info = {}
            info["thuid"] = volunteer.THUID
            info["name"] = volunteer.NAME
            info["DEPARTMENT".lower()] = volunteer.DEPARTMENT
            info["NICKNAME".lower()] = volunteer.NICKNAME
            info["SIGNATURE".lower()] = volunteer.SIGNATURE
            info["PHONE".lower()] = volunteer.PHONE
            info["VOLUNTEER_TIME".lower()] = volunteer.VOLUNTEER_TIME
            info["EMAIL".lower()] = volunteer.EMAIL
            info["rank"] = order
            order += 1
            new_top_100_list.append(info)
        ranking_top_100_list = new_top_100_list
        ranking_last_update_time = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
    return JsonResponse({"list":ranking_top_100_list, "last_update_time":str(ranking_last_update_time)}, safe=False)

# 分配志愿工时（志愿中心/志愿团体）

def allocate_volunteerhours(request):
    # raiseNotImplementedError("Not implemented!")
    if checkUserType(request) in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        # hours = json.loads(request.body)["hours"]
        activity_id = json.loads(request.body)["activity_id"]
        # volunteer_id = json.loads(request.body)["volunteer_id"]
        info = json.loads(request.body)["list"]
        activity = showactivity_models.Activity.objects.select_for_update().get(id = activity_id)
        for obj in info:
            student_id = obj["student_id"]
            student = VOLUNTEER.objects.select_for_update().get(pk = student_id)  # 不确定传过来的是id还是THUID，先这样写吧orz 
            try:
                membership = Membership.objects.select_for_update().get(volunteer=student, activity=activity, state=ENROLL_STATE_CONST["ACCEPTED"], alreadyAssignedVolunteerHour=False)
                time = obj["time"]
                totalTime = student.VOLUNTEER_TIME + time
                student.VOLUNTEER_TIME = totalTime
                student.save()
                membership.alreadyAssignedVolunteerHour=True
                membership.save()
            except:
                traceback.print_exc()
                return HttpResponse("Can't allocate to this student!", status=401)   
        return HttpResponse("Allocate volunteer hours successful!", status=200)
    else:
        return HttpResponse("Not authenticated!", status=401)    
        
# 发布反馈

def post_feedback(request):
    usertype = checkUserType(request)
    if usertype != PERMISSION_CONST["VOLUNTEER"]:
        return HttpResponse("NOT VOLUNTEER", status=401)
    else:
        try:
            THUID = checkSessionValid(request)[1]
            volunteer = VOLUNTEER.objects.select_for_update().get(THUID=THUID)
            activity_id = json.loads(request.body)["id"]
            activity = Activity.objects.select_for_update().get(id=activity_id)
            try:
                membership = Membership.objects.select_for_update().get(activity=activity, volunteer=volunteer)
                checkin.objects.select_for_update().get(membership=membership)
            except:
                traceback.print_exc()
                return JsonResponse({"success":False, FAIL_INFO_KEY:"You've not checked in!"}, status=400) # 签到之后才可以进行反馈
            if membership.already_feedback_provided:
                return JsonResponse({"success":False, FAIL_INFO_KEY:"You've already provided feedback!"}, status=400)
            else:
                membership.feedback = json.dumps({"title":json.loads(request.body)["title"], "detail":json.loads(request.body)["detail"]})
                membership.already_feedback_provided = True
                membership.feedback_time = str((datetime.datetime.utcnow()+datetime.timedelta(hours=8)).replace(tzinfo=utc)).split('.')[0]
                membership.save()
                return HttpResponse("SUCCESS")
        except:
            traceback.print_exc()
            return HttpResponse("zxwtql", status=500)

# 志愿团体或志愿中心查看活动反馈

def query_feedback(request):
    usertype = checkUserType(request)
    if not (usertype in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]):
        return HttpResponse("NOT TEACHER OR ORGANIZATION!", status=401)
    else:
        activity_id = json.loads(request.body)["id"]
        activity = Activity.objects.select_for_update().get(id=activity_id)
        if activity.ActivityOrganizer != request.user:
            return JsonResponse({"success":False, FAIL_INFO_KEY:"Not your activity!"}, status=401)
        resList = []
        for membership in Membership.objects.select_for_update().filter(activity=activity):
            if membership.already_feedback_provided:
                volunteer = membership.volunteer
                res = {}
                res["id"] = membership.id
                res["title"] = json.loads(membership.feedback)["title"]
                res["detail"] = json.loads(membership.feedback)["detail"]
                res["time"] = membership.feedback_time
                res["author"] = volunteer.THUID
                res["status"] = membership.already_feedback_read
                res["already_feedback_read"] = "已读" if membership.already_feedback_read else "未读"
                resList.append(res)
        return JsonResponse({"success":True, "list":resList})


# 志愿团体或志愿中心标记活动反馈为已读
def read_feedback(request):
    usertype = checkUserType(request)
    if not (usertype in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]):
        return HttpResponse("NOT TEACHER OR ORGANIZATION!", status=401)
    else:
        feedback_id = json.loads(request.body)["id"]
        record = Membership.objects.select_for_update().get(id=feedback_id)
        if record.activity.ActivityOrganizer != request.user:
            return JsonResponse({"success":False, FAIL_INFO_KEY:"Not your activity!"}, status=401)
        record.already_feedback_read = True
        record.save()
        return HttpResponse("SUCCESS")


# 志愿团体或志愿中心删除活动

def delete_activity(request):
    usertype = checkUserType(request)
    if usertype in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        activity_id = json.loads(request.body)["id"]
        activity = Activity.objects.select_for_update().get(id=activity_id)
        if activity.ActivityOrganizer != request.user:
            return HttpResponse("Not your activity!", status=401)
        activity.delete()
        return HttpResponse("SUCCESS", status=200)
    else:
        return HttpResponse("Failed to delete activity", status = 401)

# 返回志愿者对某个活动的签到记录
def getVolunteerCheckinRecord(request):
    usertype = checkUserType(request)
    if usertype == PERMISSION_CONST['VOLUNTEER']:
        THUID = checkSessionValid(request)[1]
        volunteer = VOLUNTEER.objects.select_for_update().get(THUID=THUID)
        activity_id = json.loads(request.body)["id"]
        activity = Activity.objects.select_for_update().get(id=activity_id)
        record = Membership(activity=activity, volunteer=volunteer)
        try:
            checkin.objects.select_for_update().get(membership=record)
            return JsonResponse({"checked": True})
        except:
            return JsonResponse({"checked": False})
    else:
        return HttpResponse("Not a volunteer", status = 401)

# 返回志愿者对某个活动的反馈记录
def getVolunteerFeedbackRecord(request):
    usertype = checkUserType(request)
    if usertype == PERMISSION_CONST['VOLUNTEER']:
        THUID = checkSessionValid(request)[1]
        volunteer = VOLUNTEER.objects.select_for_update().get(THUID=THUID)
        activity_id = json.loads(request.body)["id"]
        activity = Activity.objects.select_for_update().get(id=activity_id)
        record = Membership(activity=activity, volunteer=volunteer)
        return JsonResponse({"finished": record.already_feedback_provided})
    else:
        return HttpResponse("Not a volunteer", status = 401)

# 查看某个活动的签到记录(参观清华可能会用到这个接口)
def getActivityCheckinRecord(request):
    usertype = checkUserType(request)
    if usertype in [PERMISSION_CONST['TEACHER'], PERMISSION_CONST['ORGANIZATION']]:
        activity_id = Activity.objects.select_for_update().get
        resList = []
        activity = Activity.objects.select_for_update().get(id=activity_id)
        if activity.ActivityOrganizer != request.user:
            return HttpResponse("Not your activity!", status = 401)
        volunteers = activity.members
        for volunteer in volunteers.select_for_update().all():
            try:
                checkin_record = checkin.objects.select_for_update().get(membership = Membership.object.select_for_update().get(volunteer=volunteer, activity=activity))
                res = {}
                res["THUID"] = volunteer.THUID
                res["NAME"] = volunteer.NAME
                res["ADDRESS"] = checkin_record.address
                res["CHECKIN_TIME"] = checkin_record.checkinTime
                resList.append(res)
            except:
                pass
        return JsonResponse({"list": resList}, safe=False)
    else:
        return HttpResponse("NOT A TEACHER OR ORGANIZATION!", status = 401)
