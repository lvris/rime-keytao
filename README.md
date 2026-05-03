个人自用方案，修改自[星空键道6](https://github.com/xkinput/KeyTao)

# 主要修改

## 方案调整

`keytao.schema.yaml`
- 改用 "avuio" 引导特殊输入
  - a 引导 ";" 快符，两码顶功
  - v 引导重复输入，一码顶功
  - u 引导计算和数字大写，如 "u1" -> "一"
  - i 引导两分拆字，使用键道拼音，如 "ihlhl" -> "炎"
  - o 引导非常用特殊符号和 lua 功能
- 改用分号次选，字符集只包含字母和分号

## 字词调整

`supplement.dict.yaml` 
- 一简删除了形码词条，"avuio" 不引导单字，减少顶功之前的干扰
- 一些次选字词调整

`css.dict.yaml`
- 630 根据个人习惯调整了部分词
- 所有两字符词都增加次选，如 "ba" -> "不能"、"比如"

`keytao.phrase.dict.yaml`
- 630 让码，优化码长
- qh 编码段原本存在拼音为 zhai（摘…）与拼音为 que（缺、却…）的重码，将 zhai 强制飞键为 fh

`keytao.single.dict.yaml`
- 二简让码，优化码长
