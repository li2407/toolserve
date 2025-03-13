import os
import json
import sys
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.server import server, data

@server
def server_fun(request_method, request_data):
    """
    处理服务器请求的核心函数
    :param request_method: 请求方法（GET/POST/PUT/DELETE）
    :param request_data: 请求数据
    """
    print(f"请求方法: {request_method}, 请求数据: {request_data}")

def extract_request_data(request):
    """
    根据请求方法提取请求数据
    :param request: Django 请求对象
    :return: 提取后的数据（字典或单个值）
    """
    if request.method == 'GET':
        return request.GET.dict()  # 获取 GET 请求参数
    elif request.method == 'POST':
        return request.POST.dict()  # 获取 POST 表单数据
    elif request.method in ['PUT', 'DELETE']:
        try:
            return json.loads(request.body)  # 解析 JSON 数据
        except json.JSONDecodeError:
            print("JSON 解析失败")
            return {}
    else:
        print(f"不支持的请求方法: {request.method}")
        return None

@csrf_exempt
def app_package(request):
    """
    处理 app_package 请求的视图函数
    :param request: Django 请求对象
    :return: HTTP 响应
    """
    # 提取请求数据
    request_data = extract_request_data(request)
    if request_data is None:
        return HttpResponse(json.dumps({"error": "不支持的请求方法"}), content_type='application/json', status=400)

    # 调用服务器处理函数
    server_fun(request.method, request_data)

    # 返回响应
    return HttpResponse(json.dumps(data), content_type='application/json')