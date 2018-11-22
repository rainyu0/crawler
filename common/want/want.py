# -*- coding: utf-8 -*-
import mimetools

import config
from .utils import *
from .compat import json


class Want():
    def __init__(self, ak, sk, type='TOP', upload_endpoint=config.UPLOAD_ENDPOINT,
                 manage_endpoint=config.MANAGE_ENDPOINT):
        '''Description : 文件上传对象.

        Input : AK: 开发者的AccessKeyId

                SK: 开发者的AccessKeySecret

                type: 开发者的服务类型(即AK/SK的颁发类型，百川用户都是TOP)，可不填写。

                `upload_endpoint`和`manage_endpoint`一般不需要填写，使用默认值即可。

        '''
        self.__ak = ak
        self.__sk = sk
        self.__type = type
        self.upload_endpoint = upload_endpoint
        self.manage_endpoint = manage_endpoint
        self.http_client = WantHttp()
        self.boundary = mimetools.choose_boundary()

    def upload_file(self, policy, dir, name, file_path, md5=None, meta={}, var={}):
        '''Description : 小文件上传接口，直接传入本地文件.

        Input : policy  - 上传策略
                dir - 上传文件的存储路径
                name - 上传文件的存储文件名
                file_path - 要上传的本地文件路径
                md5 - 文件md5值（可选）
                meta - meta信息（可选）
                var - 自定义kv信息对（可选）

        Output : 上传结果的dict对象
        '''
        self.__check_args({'dir': dir, 'name': name, 'file_path': file_path})
        with open(file_path, 'rb') as f:
            return self.upload_content(policy, dir, name, f.read(), md5, meta, var)


    def upload_content(self, policy, dir, name, content, md5=None, meta={}, var={}):
        '''Description : 小文件上传接口，通过输入流上传.

        Input : policy  - 上传策略
                dir - 上传文件的存储路径
                name - 上传文件的存储文件名
                content - 要上传文件的输入流
                md5 - 文件md5值（可选）
                meta - meta信息（可选）
                var - 自定义kv信息对（可选）

        Output : 上传结果的dict对象
        '''
        self.__check_args({'dir': dir, 'name': name, 'content': content})
        self.__check_policy(policy)

        size = len(content)
        if size > config.SUB_OBJ_SIZE:
            raise WantException('file is too large, use multi part upload please')

        token = self.__upload_token(policy)

        fields = {'name': name, 'dir': dir, 'content': content, 'size': str(size)}
        if md5:
            fields['md5'] = md5
        self.__metavars('meta', meta, fields)
        self.__metavars('var', var, fields)

        return self.http_client.post('%s%s' % (self.upload_endpoint, config.UPLOAD_API_UPLOAD),
                                     self.__encode_multipart(fields),
                                     self.__make_post_headers(token))


    def multipart_init(self, policy, dir, name, content, md5=None, meta={}, var={}, size=None):
        '''Description : 分片上传初始化.

        Input : policy  - 上传策略
                dir - 上传文件的存储路径
                name - 上传文件的存储文件名
                content - 要上传文件的输入流
                md5 - 文件md5值（可选）
                meta - meta信息（可选）
                var - 自定义kv信息对（可选）

        Output : 初始化分片结果的dict对象
        '''
        self.__check_args({'dir': dir, 'name': name, 'content': content})
        self.__check_policy(policy)

        size = len(content)
        if size > config.SUB_OBJ_SIZE:
            raise WantException('multipart file is too large')

        token = self.__upload_token(policy)

        fields = {'name': name, 'dir': dir, 'content': content, 'size': str(size)}
        if md5:
            fields['md5'] = md5
        self.__metavars('meta', meta, fields)
        self.__metavars('var', var, fields)
        result = self.http_client.post('%s%s' % (self.upload_endpoint, config.UPLOAD_API_BLOCK_INIT),
                                       self.__encode_multipart(fields),
                                       self.__make_post_headers(token))
        return result


    def multipart_upload(self, policy, _id, upload_id, part_number, content, md5=None, size=None):
        '''Description : 分片上传内容.

        Input : policy  - 上传策略
                id - 上传唯一id（初始化分片任务时返回）
                upload_id - 分片上传id（初始化分片任务时返回）
                part_number - 上传块编号（分片任务初始块编号为1，之后每次上传编号加1）
                content - 要上传文件的输入流
                md5 - 文件md5值（可选）

        Output : 上传结果的dict对象
        '''
        self.__check_args({'id': _id, 'upload_id': upload_id, 'part_number': part_number, 'content': content})
        self.__check_policy(policy)

        size = len(content)
        if size > config.SUB_OBJ_SIZE:
            raise WantException('multipart file is too large')

        token = self.__upload_token(policy)

        fields = {'id': _id, 'uploadId': upload_id, 'partNumber': part_number, 'content': content, 'size': str(size)}
        if md5:
            fields['md5'] = md5
        result = self.http_client.post('%s%s' % (self.upload_endpoint, config.UPLOAD_API_BLOCK_UPLOAD),
                                       self.__encode_multipart(fields),
                                       self.__make_post_headers(token))
        return result

    def multipart_complete(self, policy, _id, upload_id, parts, md5=None):
        '''Description : 分片上传完成.

        Input : policy  - 上传策略
                id - 上传唯一id（初始化分片任务时返回）
                upload_id - 分片上传id（初始化分片任务时返回）
                parts - 每个分片md5值组成的json数组，需要进行base64的编码.例如：base64.urlsafe_b64encode(json.dumps([{'e_tag': '分片1返回的e_tag', 'part_number': 1}, {'e_tag': '分片2返回的e_tag', 'part_number': 2},
                             {'e_tag': '分片3返回的e_tag', 'part_number': 3}]))
                md5 - 完整文件的md5值（可选）

        Output : 上传结果的dict对象
        '''
        self.__check_args({'id': _id, 'upload_id': upload_id, 'md5 parts': parts})
        self.__check_policy(policy)

        token = self.__upload_token(policy)
        try:
            for p in parts:
                p['eTag'] = p.pop('e_tag')
                p['partNumber'] = p.pop('part_number')
        except Exception:
            raise WantException('invalid parts  : %s' % parts)

        fields = {'id': _id, 'uploadId': upload_id, 'parts': base64_urlsafe_encode(json.dumps(parts))}
        if md5:
            fields['md5'] = md5
        result = self.http_client.post('%s%s' % (self.upload_endpoint, config.UPLOAD_API_BLOCK_COMPLETE),
                                       self.__encode_multipart(fields),
                                       self.__make_post_headers(token))
        return result


    def multipart_cancel(self, policy, _id, upload_id):
        '''Description : 分片上传取消.

        Input : policy  - 上传策略
                id - 上传唯一id（初始化分片任务时返回）
                upload_id - 分片上传id（初始化分片任务时返回）

        Output : None
        '''
        self.__check_args({'id': _id, 'upload_id': upload_id})
        self.__check_policy(policy)

        token = self.__upload_token(policy)
        fields = {'id': _id, 'uploadId': upload_id}
        result = self.http_client.post('%s%s' % (self.upload_endpoint, config.UPLOAD_API_BLOCK_CANCEL),
                                       self.__encode_multipart(fields),
                                       self.__make_post_headers(token))
        return result


    def __upload_token(self, policy):
        try:
            encoded_policy = base64_urlsafe_encode(json.dumps(policy))
            sign = hmac_sha1(self.__sk, encoded_policy)
            token = 'UPLOAD_AK_' + self.__type + ' ' + base64_urlsafe_encode(
                self.__ak + ':' + encoded_policy + ':' + sign)
            return token
        except Exception, e:
            raise WantException(str(e))

    def __check_policy(self, policy):
        self.__check_args({'upload_policy': policy, 'namespace': policy.get('namespace')})
        if set(policy.keys()) - _upload_policy:
            raise WantException('invalid policy key : %s' % ','.join(set(policy.keys()) - _upload_policy))

    def __check_args(self, args):
        for k, v in args.items():
            if not v:
                raise WantException('%s is empty' % k)


    def __metavars(self, prefix, args, fields):
        for k, v in args.items():
            fields[prefix + k] = v


    def __make_post_headers(self, token):
        headers = {'content-type': 'multipart/form-data; boundary=%s' % self.boundary,
                   'Authorization': token,
                   'User-Agent': self.__make_user_agent()}
        return headers

    def __make_user_agent(self):
        if self.__type == 'TOP':
            return config.UPLOAD_USER_AGENT + 'TAE/' + config.SDK_VERSION
        else:
            return config.UPLOAD_USER_AGENT + 'CLOUD/' + config.SDK_VERSION


    def __encode_multipart(self, fields):
        CRLF = '\r\n'
        content = fields.pop('content', '')
        data = []
        for k, v in fields.items():
            if not k or not v:
                continue
            if not isinstance(v, str):
                v = str(v)
            data.append('--' + self.boundary)
            data.append('Content-Disposition: form-data; name="%s"' % k)
            data.append('')
            data.append(v)
        if content:
            data.append('--' + self.boundary)
            data.append('Content-Disposition: form-data; name="content"; filename="%s"' % fields.get('name'))
            data.append('Content-Type: application/octet-stream')
            data.append('')
            data.append(content)
        data.append('--' + self.boundary + '--')
        data.append('')
        return CRLF.join(data)


_upload_policy = {'callbackBody', 'callbackBodyType', 'callbackHost', 'callbackUrl', 'detectMime', 'dir', 'expiration',
                  'insertOnly', 'mimeLimit', 'name', 'namespace', 'returnBody', 'returnUrl', 'sizeLimit'}
