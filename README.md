# 定制化客户关系管理系统

### 简介

销售和客户关系管理

### 更新

### 测试

### 生成密钥

    openssl genrsa -out keypair.pem 2048
    openssl rsa -in keypair.pem -pubout -out publickey.crt
    openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in keypair.pem -out pkcs8.key
