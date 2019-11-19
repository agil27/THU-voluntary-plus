from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login
from .settings import TICKET_AUTHENTICATION, WX_TOKEN_HEADER, WX_OPENID_HEADER
from .models import WX_OPENID_TO_THUID
import requests
import json

THUID_CONST="THUID"
TOKEN_CONST="TOKEN"
OPENID_CONST="OPENID"
SUCCESS_CONST="SUCCESS"

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

def loginApi(request):
    '''
    登陆接口
    '''
    if WX_OPENID_HEADER in request.META.keys(): # Case1: 微信端，POST请求，需要维护token和openid的对应关系、openid和学号的对应关系    
        '''
        检查是否数据库中存了相应OPENID到学号的映射。
        注意openid对同一用户使用同一小程序是不变的，不会过期。
        '''
        try:
            OPENID = request.POST[WX_OPENID_HEADER]
        except:
            return HttpResponse("OPENID not found erro", status=401)
        try:
            record = WX_OPENID_TO_THUID.objects.get(OPENID=OPENID)
            # 若存了相应OPENID，说明已经绑定（不过要不要考虑openid被黑客拿走这种问题。。）
            return JsonResponse(json.dumps({THUID_CONST:record.THUID}), safe=False)
        except:
            # 若未存相应OPENID到学号的映射，说明未绑定，检查是否request header里有token：
            try:
                TOKEN = request.POST[WX_TOKEN_HEADER]
                # 若token有的话就和助教服务器后端通讯，若确认token有效就保存openid和学号的关系：
                r = validateToken(TOKEN, OPENID)
                if r[SUCCESS_CONST]:
                    record = WX_OPENID_TO_THUID(OPENID=OPENID, THUID=r[THUID_CONST])
                    record.save()
                    return JsonResponse(json.dumps({"THUID":record.THUID_CONST}), safe=False)
                else:
                    return HttpResponse("TOKEN invalid", status=401)
            except:
                return HttpResponse("TOKEN invalid", status=401)
    else: # Case2: PC端，GET请求
        if request.user.is_authenticated: # 防止同一客户端未注销后再次发出登录请求
            return HttpResponse("You've already logged in!")
        ip = get_client_ip(request).replace('.','_')
        r = requests.get(TICKET_AUTHENTICATION+request.GET.get("ticket")+'/'+ip)
        r = parseUserInfoFromTHUAuthentication(r.text)
        login(request, r["zjh"])
        return JsonResponse(json.dumps(r), safe=False)

def bindApi(request):
    #id = request.session.get('sessionid')
    client_type = request.session.get('MicroMessenger')
    if client_type != '':
        OPENID = request.session.get('OPENID')
        wxuser = mysite_models.WX_OPENID_TO_THUID.objects.get(OPENID=OPENID)
        TOKEN = request.POST[WX_TOKEN_HEADER]
        url = "https://alumni-test.iterator-traits.com/fake-id-tsinghuaproxy/api/user/session/token" 
        data = {"token": TOKEN}
        r = requests.POST(url, data)
        js = json.loads(r.text)
        thuuser = js["user"]
        THUID = thuuser["card"]
        wxuser.update(THUID = THUID)
        wxuser.save()
        return HttpResponse("Bind successful", status=200)
    else:
        return HttpResponse("Unable to bind", status=401)

    