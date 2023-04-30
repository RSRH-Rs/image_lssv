# HoshinoBot 图片版 lssv 插件

这是一个基于 HoshinoBot 的图片版 lssv 插件，改自[原 lssv 功能](https://github.com/Ice9Coffee/HoshinoBot/tree/master/hoshino/modules/botmanage/service_manage.py)，素材和图片操作也是从[无疑佬](https://github.com/KimigaiiWuyi)的[原神插件](https://github.com/KimigaiiWuyi/GenshinUID)搬的。
~~我只是一个缝合怪 a.a~~

## 使用方法

1. 在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目

```
git clone https://github.com/RSRH-Rs/image_lssv.git
```

2. 从 github 仓库下载

- 将`image_lssv`文件夹放入`hoshino/modules`

3. 配置

- 把 **`hoshino/modules/botmanage/service_manage.py`** 这个文件删掉
- 在`hoshino/config/__bot__.py`中的`MODULES_ON`里，写入字符串`image_lssv`
- 在`__init__.py`中编辑`QUALITY`和`RANDOM_BG`，指定图像质量和是否使用随机背景


## 其他

功能还是一样的，只不过服务列表通过图片发送

**渣代码,欢迎提出改进建议~**

## 示范

[![](https://github.com/RSRH-Rs/Hoshino-plugin-image-lssv/blob/master/data/imgs/example.png)]
[![](https://github.com/madoka315/image_lssv/blob/dev/data/imgs/example_multi.png)]
