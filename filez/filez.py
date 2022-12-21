import base64
import os

import requests
from urllib3 import encode_multipart_formdata

from .schema import ConfigInfo, UserInfo


class Filez(object):
    def __init__(self, config: ConfigInfo):
        """
        初始化
        """
        # 检查配置文件是否正确
        if (
            not config.get("app_key")
            or not config.get("app_secret")
            or not config.get("host")
        ):
            raise Exception("配置文件错误")

        self.config = config
        self.access_token = None

        # base_url
        self.base_url = (
            "http"
            + ("s" if config.get("https") else "")
            + "://"
            + config.get("host")
            + "/"
            + config.get("version")
        )

    def token(self, slug: str):
        """获取用户token数据.

        Examples:
            >>> token('slug')
        Args:
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
            >>> user_create(user)

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
    def user_info(self, uid: int = None, user_slug: str = None) -> dict:
        """获取用户信息.
        通过用户id或者用户slug获取用户信息

        Examples:
            >>> user_info(uid, user_slug)

        Args:
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
    def user_list(self, page_num: int, page_size: int) -> dict:
        """获取用户列表.

        Examples:
            >>> user_list(page_num,page_size)

        Args:
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
    def team_list(self):
        """获取团队列表.

        Examples:
            >>> team_list()

        Args:

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
    def team_info(self, tid: int):
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
    def team_user_list(self, tid: int, page_num: int, page_size: int):
        """获取团队用户列表.

        Examples:
            >>> team_user_list(tid,page_num,page_size)

        Args:
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
    def file_list(self, path: str, page_num: int, page_size: int):
        """获取文件列表

        Examples:
            >>> file_list(path,page_num,page_size)

        Args:
            path:       文件路径
            page_num:   页码 从0开始
            page_size:  每页条数

        Returns:
            文件列表
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
    def file_info(self, neid: str = None, nsid: int = None, path: str = None) -> dict:
        """获取文件信息
        通过neid 或者 文件路径 获取文件信息

        Examples:
            >>> file_info(neid,path)

        Args:
            neid:   文件neid
            nsid:   空间id
            path:   文件路径

        Returns:
            文件信息
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
    def file_delete(self, neid: str = None, nsid: int = None) -> dict:
        """
        通过neid 删除文件

        Examples:
            >>> file_delete(neid,nsid)

        Args:
            neid:   文件neid
            nsid:   空间id

        Returns:
            删除结果
            {
                "errcode": 0,
                "errmsg": "ok"
            }
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
    def create_folder(self, path: str, path_type: str = None) -> dict:
        """
        创建文件夹

        Examples:
            >>> create_folder(path,path_type)

        Args:
            url:    filez创建文件夹的接口地址   例如：http://filez.xxx.com:333/v2/api/file/folder
            path:   文件夹路径
            nsid:   选择范围 ['ent', 'self'], ent 企业空间，self 个人空间

        Returns:
            创建结果
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
        self, from_nsid: int, from_neid: str, to_path: str, to_path_type: str = None
    ) -> dict:
        """
        文件复制

        Examples:
            >>> file_copy(from_nsid,from_neid,to_path,to_path_type)

        Args:
            from_nsid:  源文件空间id
            from_neid:  源文件neid
            to_path:    目标文件路径
            to_path_type:   目标文件路径类型

        Returns:
            复制结果
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
        self, from_nsid: int, from_neid: str, to_path: str, to_path_type: str = None
    ) -> dict:
        """
        文件移动

        Examples:
            >>> file_move(from_nsid,from_neid,to_path,to_path_type)

        Args:
            from_nsid:  源文件空间id
            from_neid:  源文件neid
            to_path:    目标文件路径
            to_path_type:   目标文件路径类型

        Returns:
            移动结果
            {
                "errcode": 0,
                "errmsg": "ok"
            }

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
    def file_upload(self, file_path: str, to_path: str, path_type: str = None) -> dict:
        """
        文件上传(单文件)

        Examples:
            >>> file_upload(file_path, to_path, path_type)

        Args:
            file_path:  文件路径
            to_path:    目标文件路径
            path_type:  目标文件路径类型

        Returns:
            上传结果
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
