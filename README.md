# Offline Transfer
> ### Transferring words via QR Code.

#### 应用场景
* **少量文本传输**
    - 比如传输网页链接
* **无网络连接或不想连接**
    - 比如流量告罄
* **不想使用大型第三方软件**
    - 比如不想用Q*

#### 使用方法（以手机与电脑为例）
* 手机→电脑
    - ①手机用效率工具生成二维码
    - ②电脑运行python程序进行识别
    - ③复制粘贴识别结果
* 电脑→手机
    - ①电脑运行python程序生成二维码
    - ②手机用相机扫描二维码（以iPhone为例）
    - ③复制粘贴文本

#### 脚本运行相关
* python 3.7.0
* major packages
    - opencv-python
    - PyQt5
    - pyzbar
    - qrcode
