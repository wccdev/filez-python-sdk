"""Python版FileZ的操作接口.

#### 用户相关接口
    - user_create 创建用户
    - user_info 获取用户信息
    - user_list 获取用户列表

#### 团队相关接口
    - team_list 获取团队列表
    - team_info 获取团队信息
    - team_user_list 获取团队成员列表

#### 文件相关接口
    - file_list 获取指定目录的文件列表
    - file_info 获取文件信息
    - file_delete 删除文件
    - create_folder 创建文件夹
    - file_copy 复制文件
    - file_move 移动文件
    - file_upload 上传文件
    - file_rename 重命名文件
    - file_history 文件历史版本
    - file_preview 文件预览
    - file_download 文件下载

#### 授权相关接口
    - auth_create 文件授权
    - auth_delete 取消文件授权
    - auth_list 获取文件授权列表

"""

import base64
import json
import os

import requests
from urllib3 import encode_multipart_formdata

from .schema import UserInfo


class Filez(object):
    def __init__(
        self,
        *args,
        app_key: str,
        app_secret: str,
        https: bool = False,
        host: str,
        version: str = "v2",
    ):
        """
        初始化

        Examples:
            >>> filez = Filez(
            >>>            app_key = "94b4b6c69e404c2896382d8e0c91121",
            >>>            app_secret = "51661ca0-38d1-4c87-8805-794211292",
            >>>            https =  False,
            >>>            host = "filez.xxx.com:3333",
            >>>            version =  "v2",
            >>>    )

        Args:
            app_key:    应用的app_key
            app_secret: 应用的app_secret
            https:      是否使用https
            host:       filez的 域名+端口 例如：filez.xxx.com:3333
            version:    filez的API版本

        """
        # 检查配置文件是否正确
        if not app_key or not app_secret or not host:
            raise Exception("app_key,app_secret,host不能为空")

        self.app_key = app_key
        self.app_secret = app_secret
        self.https = https
        self.host = host
        self.version = version

        self.access_token = None

        # base_url
        self.base_url = "http" + ("s" if https else "") + "://" + host + "/" + version

    def token(self, slug: str) -> str:
        """获取用户token数据.

        Examples:
            >>> token(slug = 'aiden')

        Args:
            slug:   登录用户名   例如：admin

        Returns:
            用户的token数据
        """
        # 设置 Authorization
        authorization = base64.b64encode(
            (self.app_key + ":" + self.app_secret).encode("utf-8")
        ).decode("utf-8")

        # 设置payload
        payload = {'grant_type': 'client_with_su', 'scope': 'all', 'slug': slug}

        # 设置headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + authorization,
        }

        url = self.base_url + "/oauth/token"

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
            raise Exception(response.text)

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

    ############################# 用户相关接口 #############################
    @check_token
    def user_create(self, user: UserInfo) -> dict:
        """创建用户.

        Examples:
            >>> user = UserInfo(
            >>>     email="10025@qq.com",
            >>>     mobile="13812342345",
            >>>     password="123456",
            >>>     user_name="user025",
            >>>     user_slug="user025",
            >>> )
            >>> user_create(user)
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


        Args:
            user:      用户信息

        Returns:
            用户信息
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }
        payload = user.dict()

        url = self.base_url + "/user"

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def user_info(self, *args, uid: int = None, user_slug: str = None) -> dict:
        """获取用户信息.
        通过用户id或者用户slug获取用户信息

        Examples:
            >>> user_info(uid=152)
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

            >>> user_info(user_slug="user025")
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

        Args:
            uid:        用户id
            user_slug:  用户slug

        Returns:
            获取的用户信息

        """

        # url最后如果有/，则去掉
        url = self.base_url + "/api/user"

        if uid is None and user_slug is None:
            raise Exception("uid和user_slug不能同时为空")

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
            raise Exception(response.text)

        return response.json()

    @check_token
    def user_list(self, *args, page_num: int, page_size: int) -> dict:
        """获取用户列表.

        Examples:
            >>> user_list(page_num=0,page_size=2)
            {
                "errcode": 0,
                "errmsg": "ok",
                "total": 2,
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

        Args:
            page_num:   页码 从0开始
            page_size:  每页条数

        Returns:
            用户列表

        """

        # url
        url = self.base_url + "/api/user"

        url = url + "?page_num=" + str(page_num) + "&page_size=" + str(page_size)

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
            raise Exception(response.text)

        return response.json()

    ############################# 团队相关接口 #############################

    @check_token
    def team_list(self) -> dict:
        """获取团队列表.

        Examples:
            >>> team_list()
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


        Returns:
            团队列表

        """
        url = self.base_url + "/api/team"

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
            raise Exception(response.text)

        return response.json()

    @check_token
    def team_info(self, tid: int) -> dict:
        """获取团队信息.

        Examples:
            >>> team_info(tid=2)
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

        Args:
            tid:        团队id

        Returns:
            团队信息

        """
        # url
        url = self.base_url + "/api/team/" + str(tid)

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
            raise Exception(response.text)

        return response.json()

    @check_token
    def team_user_list(self, tid: int, page_num: int, page_size: int) -> dict:
        """获取团队用户列表.

        Examples:
            >>> team_user_list(tid=2,page_num=0,page_size=2)
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

        Args:
            tid:        团队id
            page_num:   页码 从0开始
            page_size:  每页条数

        Returns:
            团队用户列表

        """
        url = self.base_url + "/api/teamuser/"

        # http://xxx/v2/api/teamuser/2/users?page_num=0&page_size=50
        url = (
            url
            + str(tid)
            + "/users?page_num="
            + str(page_num)
            + "&page_size="
            + str(page_size)
        )

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
            raise Exception(response.text)

        return response.json()

    ############################# 文件相关接口 #############################
    @check_token
    def file_list(self, path: str, page_num: int, page_size: int) -> dict:
        """获取文件列表

        Examples:
            >>> file_list(path="/demo1/aa1",page=0,page_size=2)
            {
                "errcode": 0,
                "errmsg": "ok",
                "fileModelList": [
                    {
                        "bookmarkId": null,
                        "creator": "我",
                        "creatorUid": 4,
                        "deliveryCode": "",
                        "desc": "",
                        "dir": false,
                        "isBookmark": false,
                        "isTeam": null,
                        "modified": "2022-12-05T17:19:39+0800",
                        "neid": 1599694982598365196,
                        "nsid": 1,
                        "path": "xx.docx",
                        "pathType": "ent",
                        "rev": "48a728b380074a20852eb27d2ada442c",
                        "size": "200.9 KB",
                        "supportPreview": true,
                        "updator": "我",
                        "updatorUid": 4
                    },
                    {
                        "bookmarkId": null,
                        "creator": "我",
                        "creatorUid": 4,
                        "deliveryCode": "",
                        "desc": "",
                        "dir": true,
                        "isBookmark": false,
                        "isTeam": false,
                        "modified": "2022-01-09T15:25:09+0800",
                        "neid": 1571031914175795279,
                        "nsid": 1,
                        "path": "/demo1/aa1",
                        "pathType": "ent",
                        "rev": "",
                        "size": "0.0 bytes",
                        "supportPreview": false,
                        "updator": "我",
                        "updatorUid": 4
                    }
                ],
                "total": 2
            }

        Args:
            path:       文件路径
            page_num:   页码 从0开始
            page_size:  每页条数

        Returns:
            文件列表

        """
        url = self.base_url + "/api/file"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        payload = {
            'path': path,
            'path_type': 'ent',
            'page_num': page_num,
            'page_size': page_size,
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_info(self, neid: str = None, nsid: int = 1, path: str = None) -> dict:
        """获取文件信息
        通过neid 或者 文件路径 获取文件信息

        Examples:
            >>> file_info(neid=1599694982598365196,nsid=1)
            {
                "errcode": 0,
                "errmsg": "ok",
                "fileModel": {
                    "bookmarkId": null,
                    "creator": "我",
                    "creatorUid": 4,
                    "deliveryCode": "",
                    "desc": "",
                    "dir": false,
                    "isBookmark": false,
                    "isTeam": null,
                    "modified": "2022-12-05T17:19:39+0800",
                    "neid": 1599694982598365196,
                    "nsid": 1,
                    "path": "xx.docx",
                    "pathType": "ent",
                    "rev": "48a728b380074a20852eb27d2ada442c",
                    "size": "200.9 KB",
                    "supportPreview": true,
                    "updator": "我",
                    "updatorUid": 4
                }
            }
            >>> file_info(path="/demo1/aa1/xx.docx")
            {
                "errcode": 0,
                "errmsg": "ok",
                "fileModel": {
                    "bookmarkId": null,
                    "creator": "我",
                    "creatorUid": 4,
                    "deliveryCode": "",
                    "desc": "",
                    "dir": false,
                    "isBookmark": false,
                    "isTeam": null,
                    "modified": "2022-12-05T17:19:39+0800",
                    "neid": 1599694982598365196,
                    "nsid": 1,
                    "path": "/demo1/aa1/xx.docx",
                    "pathType": "ent",
                    "rev": "48a728b380074a20852eb27d2ada442c",
                    "size": "200.9 KB",
                    "supportPreview": true,
                    "updator": "我",
                    "updatorUid": 4
                }
            }

        Args:
            neid:   文件neid
            nsid:   空间id
            path:   文件路径

        Returns:
            文件信息

        """
        url = self.base_url + "/api/file"

        if neid is None and path is None:
            raise Exception("neid和path不能同时为空")

        if neid is not None:
            if nsid is None:
                nsid = 1  # 做一次默认值处理
            url = url + "/" + str(neid) + "/?nsid=" + str(nsid)
        else:
            url = url + "/path"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        if neid is None:
            payload = {'path': path, 'path_type': 'ent'}

            try:
                response = requests.request("POST", url, headers=headers, data=payload)
            except ConnectionError:
                # print(e)
                raise Exception("url检测异常，请检查url是否正确")
            except Exception:
                raise Exception("未知异常")

        else:
            try:
                response = requests.request("GET", url, headers=headers)
            except ConnectionError:
                # print(e)
                raise Exception("url检测异常，请检查url是否正确")
            except Exception:
                raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_delete(self, nsid: int, neid: str) -> dict:
        """
        通过neid 删除文件

        Examples:
            >>> file_delete(nsid=1,neid="1596056484678996029")
            {
                "errcode": 0,
                "errmsg": "ok"
            }

        Args:
            neid:   文件neid
            nsid:   空间id

        Returns:
            删除结果

        """
        url = self.base_url + "/api/file"

        if neid is None:
            raise Exception("neid不能为空")

        if nsid is None:
            nsid = 1  # 做一次默认值处理

        url = url + "/" + str(neid) + "?nsid=" + str(nsid)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        try:
            print(url)
            response = requests.request("DELETE", url, headers=headers)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def create_folder(self, path: str, path_type: str = "ent") -> dict:
        """
        创建文件夹

        Examples:
            >>> create_folder(path="/demo2/dir1/dir2",path_type="ent")
            {
                "creator": "",
                "creatorUid": 4,
                "desc": "",
                "dir": true,
                "errcode": 0,
                "errmsg": "ok",
                "modified": "2022-12-20 15:18:00",
                "neid": 1605100184113516618,
                "nsid": 1,
                "path": "/demo2/dir1/dir2",
                "pathType": "ent",
                "rev": "",
                "size": "",
                "updator": "",
                "updatorUid": 4
            }

        Args:
            path:        文件夹路径
            path_type:   选择范围 ['ent', 'self'], ent 企业空间，self 个人空间

        Returns:
            创建结果

        """
        url = self.base_url + "/api/file/folder"

        if path_type is None:
            path_type = "ent"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        payload = {'path': path, 'path_type': path_type}

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_copy(
        self, from_nsid: int, from_neid: str, to_path: str, to_path_type: str = "ent"
    ) -> dict:
        """
        文件复制

        Examples:
            >>> file_copy(from_nsid=1,from_neid="1564548230711087165",to_path="/demo3/dd2",to_path_type="ent") # noqa
            {
                "creator": "我",
                "creatorUid": 4,
                "desc": "",
                "dir": false,
                "errcode": 0,
                "errmsg": "ok",
                "modified": "2022-12-21 10:52:07",
                "neid": 1605395663741259776,
                "nsid": 1,
                "path": "/demo3/dd2/313.doc",
                "pathType": "ent",
                "rev": "abb44e2a31124c018a6062798eb6bd10",
                "size": "10.07 KB",
                "updator": "我",
                "updatorUid": 4
            }

        Args:
            from_nsid:  源文件空间id
            from_neid:  源文件neid
            to_path:    目标文件路径
            to_path_type:   目标文件路径类型

        Returns:
            复制结果

        """
        url = self.base_url + "/api/file/copy"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        if to_path_type is None:
            to_path_type = "ent"

        payload = {
            'nsid': from_nsid,
            'from_neid': from_neid,
            'to_path': to_path,
            'to_path_type': to_path_type,
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_move(
        self, from_nsid: int, from_neid: str, to_path: str, to_path_type: str = "ent"
    ) -> dict:
        """
        文件移动

        Examples:
            >>> file_move(from_nsid=1,from_neid="1565591868459192393",to_path="/demo3/dd2",to_path_type="ent") # noqa
            {
                "errcode": 0,
                "errmsg": "ok"
            }

        Args:
            from_nsid:  源文件空间id
            from_neid:  源文件neid
            to_path:    目标文件路径
            to_path_type:   目标文件路径类型

        Returns:
            移动文件的结果

        """
        url = self.base_url + "/api/file/move"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        if to_path_type is None:
            to_path_type = "ent"

        payload = {
            'nsid': from_nsid,
            'from_neid': from_neid,
            'to_path': to_path,
            'to_path_type': to_path_type,
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_upload(self, file_path: str, to_path: str, path_type: str = "ent") -> dict:
        """
        文件上传(单文件)

        Examples:
            >>> file_upload(file_path="E:/php_workspace_www/filez-python-sdk/mm.jpg",to_path="/file001/x1.jpg",path_type="ent") # noqa
            {
                "creator": "",
                "creatorUid": 4,
                "desc": "",
                "dir": false,
                "errcode": 0,
                "errmsg": "ok",
                "modified": "2022-12-21T11:11:00+0800",
                "neid": 1605400413375303763,
                "nsid": 1,
                "path": "/file001/a1.xlsx",
                "pathType": "ent",
                "rev": "d8c4f24f5370425f8b170c7eb5a41158",
                "size": "13.7 KB",
                "updator": "",
                "updatorUid": 4
            }

        Args:
            file_path:  文件路径
            to_path:    目标文件路径
            path_type:  目标文件路径类型

        Returns:
            上传结果

        """
        url = self.base_url + "/api/file/content"

        if path_type is None:
            path_type = "ent"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise Exception("文件不存在")

        file_data = {
            'filedata': (os.path.basename(file_path), open(file_path, 'rb').read()),
            'path_type': path_type,
            'path': to_path,
        }

        encode_data = encode_multipart_formdata(file_data)
        data = encode_data[0]

        headers = {
            'Content-Type': encode_data[1],
            'Authorization': 'Bearer ' + self.access_token,
        }

        try:
            response = requests.request("POST", url, headers=headers, data=data)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_rename(self, nsid: int, from_neid: str, to_file_name: str) -> dict:
        """
        文件重命名

        Examples:
            >>> file_rename(nsid=1,from_neid="1605507933683060811",to_file_name="x1.jpg") # noqa
            {
                "errcode": 0,
                "errmsg": "ok"
            }

        Args:
            nsid:               文件空间id
            from_neid:          文件neid
            to_file_name:       新文件名

        Returns:
            重命名结果

        """
        url = self.base_url + "/api/file/rename"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        payload = {
            'nsid': nsid,
            'from_neid': from_neid,
            'to_file_name': to_file_name,
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_history(self, nsid: int, neid: str) -> dict:
        """
        文件历史版本

        Examples:
            >>> file_history(nsid=1,neid="1605453934825050149")
            {
                "errcode": 0,
                "errmsg": "ok",
                "revisionModelList": [
                    {
                        "bytes": 14018,
                        "dir": false,
                        "hash": "f0fc246d3cf09e3842fea5dbc9bb57e1",
                        "isDeleted": false,
                        "modified": "2022-12-21T14:43:41+0800",
                        "op": "create",
                        "path": "/file001/a3.xlsx",
                        "rev": "0619c04dcc144938b11779a4b3a820da",
                        "root": "databox",
                        "user": "管理员",
                        "utime": 1671605021000,
                        "version": "v1"
                    },
                    {
                        "bytes": 9653,
                        "dir": false,
                        "hash": "e2271374a796f19f18bd17a0b2da65b1",
                        "isDeleted": false,
                        "modified": "2022-12-22T13:53:30+0800",
                        "op": "update",
                        "path": "/file001/a3.xlsx",
                        "rev": "5de540139dd5e04f",
                        "root": "databox",
                        "user": "管理员",
                        "utime": 1671688410000,
                        "version": "v2"
                    }
                ]
            }
        Args:
            nsid:   文件空间id
            neid:   文件neid

        Returns:
            文件历史版本记录

        """
        url = self.base_url + "/api/file/" + str(neid) + "/revision?nsid=" + str(nsid)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
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
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_preview(self, nsid: int, neid: str) -> dict:
        """
        文件预览

        Examples:
            >>> file_preview(nsid=1,neid="1605453934825050149")
            {
                "errcode": 0,
                "errmsg": "ok",
                "previewUrl": "https://filz.xx.com/preview/preview?nsid=123&neid=123&version=v1" # noqa
            }

        Args:
            nsid:   文件空间id
            neid:   文件neid

        Returns:
            文件预览信息

        """
        url = self.base_url + "/api/preview/" + str(neid) + "?nsid=" + str(nsid)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
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
            raise Exception(response.text)

        return response.json()

    @check_token
    def file_download(self, nsid: int, neid: str) -> dict:
        """
        文件下载

        Examples:
            >>> file_download(nsid=1,neid="1605453934825050149")
            文件流
        Args:
            nsid:   文件空间id
            neid:   文件neid

        Returns:
            文件下载
        """
        url = (
            self.base_url
            + "/api/file/content/download?neid="
            + str(neid)
            + "&nsid="
            + str(nsid)
        )

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
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
            raise Exception(response.text)

        # 保存文件
        return response.content

    ############################# 权限相关接口 #############################

    @check_token
    def auth_create(
        self, nsid: int, path_type: str, neid: str, privileges: list
    ) -> dict:
        """
        文件批量授权 (privileges一次建议10个以内,如果过多,请分批次调用, Filez有长度限制)

        Examples:
            >>> auth_batch_create(nsid=1,path_type="ent",neid="1605400413333360659",privileges=[{"uid":82,"privilege":2009},{"uid":83,"privilege":2001}]) #noqa
            {
                "authModelList": null,
                "errcode": 0,
                "errmsg": "ok"
            }
        Args:
            nsid:       文件空间id
            path_type:  文件类型 [ent,self]
            neid:       文件neid
            privileges:  [{"uid":82,"privilege":2009},{"uid":83,"privilege":2001}]  uid为用户id,privilege为权限id
                (权限说明 预览: 2009,上传: 2007,下载: 2005,上传/下载: 2003,编辑: 2001,可见列表: 1011,禁止访问: 1000) # noqa

        Returns:
            文件授权结果
        """
        url = self.base_url + "/api/auth/batch_create"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        if path_type not in ['ent', 'self']:
            raise Exception("path_type参数错误")

        for item in privileges:
            if item.get('privilege') not in [2009, 2007, 2005, 2003, 2001, 1011, 1000]:
                raise Exception("privilege参数错误")

        auth_list = []
        for item in privileges:
            auth_list.append(
                {
                    "agentId": item.get('uid'),
                    "agentType": "user",
                    "isSubteamInheritable": True,
                    "privilegeType": item.get('privilege'),
                }
            )

        payload = {
            'nsid': nsid,
            'path_type': path_type,
            'file_list': json.dumps([{"neid": neid}]),
            'auth_list': json.dumps(auth_list),
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def auth_delete(self, nsid: int, path_type: str, neid: str, uids: list) -> dict:
        """
        文件取消授权

        Examples:
            >>> auth_delete(nsid=1,path_type="ent",neid="1605400413333360659",uids=[82,83]) # noqa
            {
                'errcode': 0,
                'errmsg': 'ok',
                'resultList': [{
                    'errmsg': 'ok',
                    'path': '/filepath/001',
                    'result': 'succeed'
                }]
            }

        Args:
            nsid:       文件空间id
            path_type:  文件类型 [ent,self]
            neid:       文件neid
            uids:        用户id列表

        Returns:
            文件取消授权结果

        """
        url = self.base_url + "/api/auth/batch_delete"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        if path_type not in ['ent', 'self']:
            raise Exception("path_type参数错误")

        # 批量用户授权
        user_list = []
        for uid in uids:
            user_list.append(
                {
                    "agentId": uid,
                    "agentType": "user",
                }
            )

        payload = {
            'nsid': nsid,
            'path_type': path_type,
            'file_list': json.dumps([{"neid": neid}]),
            'delete_list': json.dumps(user_list),
        }

        try:
            response = requests.request("DELETE", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    @check_token
    def auth_list(self, nsid: int, path_type: str, neid: str) -> dict:
        """
        文件授权列表

        Examples:
            >>> auth_list(nsid=1,path_type="ent",neid="1605400413333360659")
            {
                "authFileList": [
                    {
                        "authList": [
                            {
                                "agentId": 130,
                                "agentName": "陈郭",
                                "agentType": "user",
                                "allowedMask": "3073",
                                "id": 14322,
                                "isSubteamInheritable": true,
                                "isTeam": false,
                                "nsid": 1,
                                "path": "/file001",
                                "privilegeId": 2009,
                                "privilegeName": "preview"
                            },
                            {
                                "agentId": 94,
                                "agentName": "陈超",
                                "agentType": "user",
                                "allowedMask": "3613",
                                "id": 14323,
                                "isSubteamInheritable": true,
                                "isTeam": false,
                                "nsid": 1,
                                "path": "/file001",
                                "privilegeId": 2005,
                                "privilegeName": "download"
                            }
                        ],
                        "inheritAuthList": [],
                        "path": "/file001"
                    }
                ],
                "errcode": 0,
                "errmsg": "ok"
            }

        Args:
            nsid:       文件空间id
            path_type:  文件类型 [ent,self]
            neid:       文件neid

        Returns:
            文件授权列表

        """
        url = self.base_url + "/api/auth/list"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + self.access_token,
        }

        if path_type not in ['ent', 'self']:
            raise Exception("path_type参数错误")

        payload = {
            'nsid': nsid,
            'path_type': path_type,
            'file_list': json.dumps([{"neid": neid}]),
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except ConnectionError:
            # print(e)
            raise Exception("url检测异常，请检查url是否正确")
        except Exception:
            raise Exception("未知异常")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()
