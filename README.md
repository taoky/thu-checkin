# 清华大学校外手动健康打卡脚本

修改自[基于 Systemd timer 的自动打卡脚本](https://github.com/iBug/thu-checkin)，为状态为「**不在校**」的同学设计，用于在保证电子身份服务系统用户名与密码不明文存储的前提下**手动**打卡，并尽可能与 Linux 桌面环境集成。

**仅含「每日打卡」功能。**

**仅在 Arch Linux + GNOME on Wayland + 1Password 上测试**，不过其他的桌面环境应该都是能用的。

## 环境要求

- 日用 Linux 桌面系统（仅在 GNOME 上测试，但是其他的桌面环境应该也能用）
  - 以下提供的 Ubuntu/Debian 配置继承自原项目，未测试。
- Tesseract
  - Arch Linux 安装 `tesseract-data-eng`
  - Ubuntu 和 Debian 可以直接使用 `apt install tesseract-ocr` 安装
- Python 3，并且安装了一些库：
  - requests（可以直接安装系统软件源提供的 `python-requests` (Arch Linux) `python3-requests` (Ubuntu/Debian) 包，也可以从 PyPI 安装，没有区别）
  - pillow（`pacman -S python-pillow` 或 `apt install python3-pil` 或 `pip3 install pillow`）
  - pytesseract（`pacman -S python-pytesseract` 或从 PyPI 安装）
- 秘密存储后端
  - keyring（`pacman -S python-keyring` 或从 PyPI 安装）
  - 1Password CLI（使用此后端需要保证到 my.1password.com 的网络畅通。如果你使用 1Password 存储电子身份服务系统密码，参考官方帮助页面 <https://developer.1password.com/docs/cli> 配置 CLI。特别地，请打开 1Password 客户端的 Biometric unlock 功能，以方便使用）
- 基于 DBus 的桌面通知（可选）
  - notify2（`pacman -S python-notify2` 或从 PyPI 安装）

## 使用方法

- 将 `thu-checkin.py` 复制到用户指定的某个目录下
- 在对应目录下创建 [`thu-checkin.txt` 文件](thu-checkin.example.txt)，填入以下内容：

    ```ini
    [thu-checkin]
    SECRET_BACKEND=使用 keyring 还是 1Password CLI "op"，对应值分别为 keyring 和 onepwd
    ONEPWD_NAME=如果使用 1Password CLI，电子身份服务系统密码对应的项名
    JUZHUDI=你所在的城市
    EMERGENCY_NAME=你的紧急联系人
    EMERGENCY_RELATION=紧急联系人和你的关系
    EMERGENCY_MOBILE=紧急联系人的电话
    SCHOOL_ABBR=学校的英文缩写，应该是 thu 吧
    USER_AGENT=浏览器的 UA，可选
    ```
- 在你想打卡的时候，执行 `./thu-checkin.py` 即可。如果选择 keyring 后端，首次执行时脚本会询问用户名与密码，并存储于 GNOME keyring（或者其他 secret 后端，如 KDE Wallet）中。
  - 如果需要桌面通知，运行时添加 `--notify` 参数。

## 许可

本项目以 MIT 协议开源，详情请见 [LICENSE](LICENSE) 文件。
