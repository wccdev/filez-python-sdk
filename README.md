<p align="center">
    <a href="https://www.filez.com/">
    <img src="https://raw.githubusercontent.com/wccdev/filez-python-sdk/master/.github/assets/logo-black.png" width="120" margin="50" alt="Python SDK For FileZ">
    </a>
</p>
<p align="center">
    <strong>
    Python SDK for
    <a href="https://www.filez.com/">Lenovo FileZ</a>
    </strong>
</p>
<p align="center">
    <a href="https://github.com/wccdev/filez-python-sdk/actions/workflows/ci.yml"><img
        src="https://github.com/wccdev/filez-python-sdk/actions/workflows/ci.yml/badge.svg"
        alt="Build"
        /></a>
    <a href="https://github.com/wccdev/filez-python-sdk/blob/main/LICENSE"><img
        src="https://img.shields.io/github/license/wccdev/filez-python-sdk"
        alt="License"
        /></a>
    <a href="https://pypi.org/project/filez-python-sdk/"><img
        src="https://img.shields.io/pypi/pyversions/filez-python-sdk.svg"
        alt="Python"
        /></a>
    <a href="https://pypi.org/project/filez-python-sdk/"><img
        src="https://img.shields.io/pypi/v/filez-python-sdk.svg"
        alt="Python Package Index"
        /></a>
    <a href="https://github.com/psf/black"><img
        src="https://img.shields.io/badge/code%20style-black-000000.svg"
        alt="Code Style"
        /></a>
</p>
<p align="center">
    Skeleton project created by Cookiecutter PyPackage.
</p>
<h2></h2>

## 文档
Skeleton project created by Cookiecutter PyPackage


* Documentation: <https://wccdev.github.io/filez-python-sdk/>
* GitHub: <https://github.com/wccdev/filez-python-sdk>
* PyPI: <xx>
* Free software: MIT


## 功能说明

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

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [wccdev/cookiecutter-pypackage](https://github.com/wccdev/cookiecutter-pypackage) project template.
