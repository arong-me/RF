*** Settings ***
Library           Selenium2Library
Resource          ../L2功能层/打开网页.txt
Resource          ../../05-资源/前置条件资源.txt
Resource          ../../05-资源/通用.txt
Resource          ../../05-资源/config.txt
Resource          ../L2功能层/登录.txt

*** Test Cases ***
打开网页
    [Template]
    打开网页    ${线上正式地址}    #打开网页
    登录    ${线上正式账户名}    ${线上正式密码}
    [Teardown]    用例失败退出操作
