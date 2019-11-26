from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login
from .settings import TICKET_AUTHENTICATION, WX_TOKEN_HEADER, WX_OPENID_HEADER, WX_CODE_HEADER, WX_HTTP_API, \
    WX_APPID, WX_SECRET, REDIRECT_TO_LOGIN
from .models import WX_OPENID_TO_THUID, VOLUNTEER
import requests
import json
from django.contrib.sessions.backends.db import SessionStore
import datetime 
from django.utils.timezone import utc


THUID_CONST="THUID"
TOKEN_CONST="TOKEN"
OPENID_CONST="OPENID"
SUCCESS_CONST="SUCCESS"
LOGGED_IN_CONST="LOGGED_IN"

def redirectToTHUAuthentication(request):
    #TODO: 防止同一客户端未注销后再次发出登录请求
    if False:
        raise NotImplementedError
    return HttpResponseRedirect(REDIRECT_TO_LOGIN)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def parseUserInfoFromTHUAuthentication(text):
    parsed = {}
    for r in text.split(':'):
        prop = r.split('=')[0]
        value = r.split('=')[1]
        parsed[prop] = value
    return parsed

def getOpenID(request):
    raise NotImplementedError

def validateToken(token, openid):
    raise NotImplementedError
    return {SUCCESS_CONST:True, THUID_CONST:"2016110011"}

def checkSessionValid(request):
    '''
    检查用户是否登录、登录是否过期，若登录且未过期返回True，否则返回False
    '''
    client_type = request.META['HTTP_USER_AGENT']
    try:
        if "MicroMessenger" in client_type:
            sessionid = request.META["HTTP_SET_COOKIE"].split("=")[1]
        else:
            sessionid = request.session.session_key
        s = SessionStore(session_key=sessionid)
        if s[LOGGED_IN_CONST]!= True:
            return False
        expiry_date = s.get_expiry_date()
        print("expiry_date: {}".format(expiry_date))
        utcnow = datetime.datetime.utcnow().replace(tzinfo=utc)
        print("utcnow: {}".format(utcnow))
        if utcnow<expiry_date:
            return True
        else:
            s[LOGGED_IN_CONST] = False
            return False
    except:
        return False

def getStudentID(request):
    '''
    获取学号，调用此函数前应调用checkSessionValid函数检查登录状态
    若获取成功则返回学号，否则返回False
    '''
    client_type = request.META['HTTP_USER_AGENT']
    if "MicroMessenger" in client_type:
        try:
            sessionid = request.META["HTTP_SET_COOKIE"].split("=")[1]
            OPENID = SessionStore(session_key=sessionid)[OPENID_CONST]
            record = WX_OPENID_TO_THUID.objects.get(OPENID = OPENID)
            THUID = record.THUID
            return THUID
        except:
            return False
    else:
        if THUID_CONST in request.session.keys():
            return request.session[THUID_CONST]
        else:
            return False

def loginApi(request):
    '''
    登陆接口
    '''
    client_type = request.META['HTTP_USER_AGENT']
    if checkSessionValid(request):
        return HttpResponse("No need to login repeatedly", status=403)
    if "MicroMessenger" in client_type: # Case 1: 微信端，POST请求
        jsonBody = json.loads(request.body)
        if WX_CODE_HEADER in jsonBody.keys(): # 处理code
            code = jsonBody[WX_CODE_HEADER]
            r = requests.post(WX_HTTP_API,data={"appid":WX_APPID, "secret":WX_SECRET, "js_code":code, "grant_type":"authorization_code"})
            res = json.loads(r.text)
            if ("errcode" not in res.keys()) or (res["errcode"] == 0):
                request.session[OPENID_CONST]=res["openid"]
                request.session[LOGGED_IN_CONST] = True
                # 检查有没有绑定
                try:
                    record = WX_OPENID_TO_THUID.objects.get(OPENID = res["openid"])
                    THUID = record.THUID
                    return JsonResponse({"THUID":THUID})
                except:
                    return JsonResponse({"THUID":"Not binded"})
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("not found WX_CODE_HEADER",status=404)
    else: # Case2: PC端，GET请求
        ip = get_client_ip(request).replace('.','_')
        r = requests.get(TICKET_AUTHENTICATION+request.GET.get("ticket")+'/'+ip)
        r = parseUserInfoFromTHUAuthentication(r.text)
        request.session[LOGGED_IN_CONST] = True
        THUID = r["zjh"]
        request.session[THUID_CONST] = THUID
        # 更新VOLUNTEER表
        try:
            VOLUNTEER.objects.get(THUID=THUID)
        except:
            volunteer = VOLUNTEER(THUID = THUID, NAME = r["xm"], DEPARTMENT=r["dw"], EMAIL=r["email"], NICKNAME = r["xm"])
            volunteer.save()
        return JsonResponse(json.dumps(r), safe=False)

def bindApi(request):
    if not checkSessionValid(request):
        return HttpResponse("You need to login!", status=401)
    client_type = request.META['HTTP_USER_AGENT']
    if "MicroMessenger" in client_type: # Case 1: 微信端，POST请求
        sessionid = request.META["HTTP_SET_COOKIE"].split("=")[1]
        s = SessionStore(session_key=sessionid)
        OPENID = s.get('OPENID')
        alreadyBinded = True # 若已经绑定，可以重新绑定
        try:
            wxuser = WX_OPENID_TO_THUID.objects.get(OPENID=OPENID)
        except:
            alreadyBinded = False
        TOKEN = json.loads(request.body)[WX_TOKEN_HEADER]
        url = "https://alumni-test.iterator-traits.com/fake-id-tsinghua-proxy/api/user/session/token"
        data = {"token": TOKEN}
        r = requests.post(url, json=data)
        r = json.loads(r.text)
        if not "error" in r.keys() or r["error"]["code"]!=0:
            return HttpResponse("Unable to bind", status=401)
        thuuser = r["user"]
        THUID = thuuser["card"]
        if alreadyBinded:
            print("rebind!")
            wxuser.THUID = THUID
            wxuser.save()
        else:
            print("bind!")
            wxuser = WX_OPENID_TO_THUID(OPENID=OPENID, THUID = THUID)
            wxuser.save()
        # 更新VOLUNTEER表
        try:
            VOLUNTEER.objects.get(THUID=THUID)
        except:
            volunteer = VOLUNTEER(THUID = THUID, NAME = thuuser["name"], DEPARTMENT=thuuser["department"], EMAIL=thuuser["mail"], NICKNAME = thuuser["name"])
            volunteer.save()
        return HttpResponse(str(THUID),status=200)
    else:
        return HttpResponse("Unable to bind for PC client", status=401)

def volunteerChangeInfo(request):
    if not checkSessionValid(request):
        return HttpResponse("You need to login!", status=401)
    THUID = getStudentID(request)
    if THUID == False:
        return HttpResponse("Failed to get THUID!", status=404)
    MODIFIABLE_PROPS = ["NICKNAME","SIGNATURE","PHONE"]
    try:
        info = VOLUNTEER.objects.get(THUID=THUID)
        body = json.loads(request.body)
        for key in body.keys():
            if key in MODIFIABLE_PROPS:
                setattr(info, key, body[key])
        info.save()
        return HttpResponse("OPERATION SUCCESS", status=200)
    except:
        return HttpResponse("OPERATION FAILED", status=404)

