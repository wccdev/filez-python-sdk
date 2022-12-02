import base64

import requests

from .schema import UserInfo


class Filez(object):
    def __init__(self, config: dict):
        """初始化.

        Args:
            config: 包含app_key,app_secret的字典 例如{"app_key":"xxx","app_secret":"
        """
        # 检查配置文件是否正确
        if not config.get("app_key") or not config.get("app_secret"):
            raise Exception("配置文件错误")

        self.config = config
        self.access_token = None

    def token(self, url: str, slug: str):
        """获取用户token数据.

        Examples:
            >>> token('url', 'slug')
        Args:
            url:    filez获取token的接口地址   例如：http://filez.xxx.cn:5555/v2/oauth/token
            slug:   登录用户名   例如：admin

        Returns:
            用户token数据
        """
        # 设置 Authorization
        authorization = base64.b64encode(
            (
                self.config.get("app_key", "") + ":" + self.config.get("app_secret", "")
            ).encode("utf-8")
        ).decode("utf-8")

        # 设置payload
        payload = {'grant_type': 'client_with_su', 'scope': 'all', 'slug': slug}

        # 设置headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + authorization,
        }

        # 发送请求
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError as e:
            print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        # 检查返回值
        if response.status_code != 200:
            raise Exception(response.json().get("error"))

        # 解析token数据
        token_data = response.json()
        if not token_data.get("access_token"):
            raise Exception("token数据异常")
        self.access_token = token_data.get("access_token")


    # 用于检查token是否存在
    def check_token(func):
        def wrapper(self, *args, **kwargs):
            if not self.access_token:
                raise Exception("请先获取token")
            return func(self, *args, **kwargs)
        return wrapper

    @check_token
    def user_create(self, url: str, user: UserInfo) -> dict:
        """创建用户.

        Examples:
            >>> user_create(url, user)

        Args:
            url:        filez创建用户的接口地址   例如：http://filez.xxx.cn:5555/v2/user
            user:      用户信息

        Returns:
            用户信息
            {
                "email": "111122@qq.com",
                "errcode": 0,
                "errmsg": "ok",
                "id": 150,
                "mobile": "",
                "quota": 107374182400,
                "status": 1,
                "used": 0,
                "userName": "user011",
                "userSlug": "user011"
            }
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }
        payload = user.dict()
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.json().get("errmsg"))

        return response.json()

    @check_token
    def user_info(self, url: str, uid: int = None, user_slug: str = None) -> dict:
        """获取用户信息.
        通过用户id或者用户slug获取用户信息

        Examples:
            >>> user_info(url, uid, user_slug)

        Args:
            url:        filez获取用户信息的接口地址   例如：http://filez.xxx.com:3333/v2/api/user
            uid:        用户id
            user_slug:  用户slug

        Returns:
            id 获取的用户信息
            {
                "email": "10025@qq.com",
                "errcode": 0,
                "errmsg": "ok",
                "id": 152,
                "mobile": "13812342345",
                "quota": 107374182400,
                "status": 1,
                "used": 0,
                "userName": "user025",
                "userSlug": "user025"
            }"

            user_slug 获取的用户信息
            {
                "ctime": "2022-12-01 18:31:07",
                "email": "10025@qq.com",
                "errcode": 0,
                "errmsg": "ok",
                "mobile": "13812342345",
                "slug": "user025",
                "uid": 152,
                "userName": "user025"
            }
        """

        # url最后如果有/，则去掉
        if url[-1] == "/":
            url = url[:-1]

        # 如果有uid则使用uid获取用户信息
        if uid:
            url = url + "/" + str(uid)

        # 如果有user_slug则使用user_slug获取用户信息
        if user_slug:
            url = url + "/slug?user_slug=" + user_slug

        headers = {
            'Authorization': 'Bearer ' + self.access_token,
        }
        try:
            response = requests.request("GET", url, headers=headers)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.json().get("errmsg"))

        return response.json()

    @check_token
    def user_list(self, url: str, page_num: int, page_size: int) -> dict:
        """获取用户列表.

        Examples:
            >>> user_list(url,page_num,page_size)

        Args:
            url:        filez获取用户列表的接口地址   例如：http://filez.xxx.com:3333/v2/api/user
            page_num:   页码 从0开始
            page_size:  每页条数

        Returns:
            用户列表
            {
                "errcode": 0,
                "errmsg": "ok",
                "total": 79,
                "userList": [
                    {
                        "email": "xx@qq.com",
                        "id": 5,
                        "mobile": "",
                        "quota": 109951162777600,
                        "status": 1,
                        "used": 11110571,
                        "userName": "xx",
                        "userSlug": "xx"
                    },
                    {
                        "email": "xx1@qq.com",
                        "id": 123,
                        "mobile": "xx",
                        "quota": 107374182400,
                        "status": 1,
                        "used": 0,
                        "userName": "xx1",
                        "userSlug": "xx1"
                    }
                ]
            }
        """

        # url最后如果没有/，则添加/
        if url[-1] != "/":
            url = url + "/"

        url = url + "?page_num=" + str(page_num) + "&page_size=" + str(page_size)

        headers = {
            'Authorization': 'Bearer '+self.access_token,
        }
        try:
            response = requests.request("GET", url, headers=headers)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.json().get("errmsg"))

        return response.json()

    @check_token
    def team_list(self,url):
        """获取团队列表.

        Examples:
            >>> team_list(url)

        Args:
            url:        filez获取团队列表的接口地址   例如：http://filez.xxx.com:3333/v2/api/team

        Returns:
            团队列表
            {
                "errcode": 0,
                "errmsg": "ok",
                "teamList": [
                    {
                        "description": "团队1",
                        "id": 2,
                        "memberLimit": 200,
                        "name": "team1",
                        "quota": 1048576000,
                        "used": 40142023
                    },
                    {
                        "description": "",
                        "id": 3,
                        "memberLimit": 10,
                        "name": "team2",
                        "quota": 10737418240,
                        "used": 0
                    }
                ],
                "total": 2
            }
        """
        headers = {
            'Authorization': 'Bearer '+self.access_token,
        }
        try:
            response = requests.request("GET", url, headers=headers)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.json().get("errmsg"))

        return response.json()

    @check_token
    def team_info(self,url,tid:int):
        """获取团队信息.

        Examples:
            >>> team_info(url,tid)

        Args:
            url:        filez获取团队信息的接口地址   例如：http://filez.xxx.com:3333/v2/api/team
            tid:        团队id

        Returns:
            团队信息
            {
                "description": "团队1",
                "errcode": 0,
                "errmsg": "ok",
                "id": 2,
                "memberLimit": 200,
                "name": "team1",
                "quota": 1048576000,
                "used": 40142023
            }
        """
        # url最后如果没有/，则添加/
        if url[-1] != "/":
            url = url + "/"

        url = url + str(tid)

        headers = {
            'Authorization': 'Bearer '+self.access_token,
        }

        try:
            response = requests.request("GET", url, headers=headers)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.json().get("errmsg"))

        return response.json()

    @check_token
    def team_user_list(self,url,tid:int,page_num:int,page_size:int):
        """获取团队用户列表.

        Examples:
            >>> team_user_list(url,tid,page_num,page_size)

        Args:
            url:        filez获取团队用户列表的接口地址   例如：http://filez.xxx.com:3333/v2/api/teamuser/
            tid:        团队id
            page_num:   页码 从0开始
            page_size:  每页条数

        Returns:
            团队用户列表
            {
                "errcode": 0,
                "errmsg": "ok",
                "memberList": [
                    {
                        "ctime": "2022-12-02T17:06:17+0800",
                        "email": "xx@qq.com",
                        "fromDomainAccount": false,
                        "path": "/team1",
                        "role": "member",
                        "status": 1,
                        "team": "team1",
                        "uid": 2,
                        "userName": "xx"
                    },
                    {
                        "ctime": "2022-12-02T17:06:17+0800",
                        "email": "xx1@qq.com",
                        "fromDomainAccount": false,
                        "path": "/team1",
                        "role": "member",
                        "status": 1,
                        "team": "team1",
                        "uid": 3,
                        "userName": "xx1"
                    }
                ],
                "total": 2
            }
        """
        if url[-1] != "/":
            url = url + "/"

        #http://xxx/v2/api/teamuser/2/users?page_num=0&page_size=50
        url = url + str(tid) + "/users?page_num=" + str(page_num) + "&page_size=" + str(page_size)

        headers = {
            'Authorization': 'Bearer '+self.access_token,
        }

        try:
            response = requests.request("GET", url, headers=headers)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.json().get("errmsg"))

        return response.json()



