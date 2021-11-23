# Django AliCloud OSS Storage

**django-oss-storage** 基于**阿里云OSS服务** 实现了[Django File storage API](https://docs.djangoproject.com/en/3.2/ref/files/storage/)


## 功能、安装、使用方式参考[官方repo](https://github.com/aliyun/django-oss-storage/)

## 新增功能

### OSS自定义域名
增加 **OSS_USER_DOMAIN** 配置项目。

```
OSS_USER_DOMAIN = "https://oss.my.domain"
```

Ps. 如果在阿里云VPC内网环境，将 OSS_ENDPOINT 配置为 OSS VPC 内网域名可以优化OSS访问。