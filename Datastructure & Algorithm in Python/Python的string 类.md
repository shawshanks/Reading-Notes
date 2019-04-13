# Python的String类各种方法及其效率
## 产生一个新的string
```python
string.capitalize()
string.center()
string.strip()
...
```
效率: O(n),跟需要产生的新字符串长度成线性关系

特别的, 条件检查的效率一般也为O(n), 但是因为短路的关系,效率可能特别快

## 模式匹配
```python
string.find()
string.index()
string.count()
string.replace()
string.split()
...
```
效率: O(mn) m为要匹配的字符串长度, n为原字符串长度

## 组合字符串
构建一个更大的新的字符方法:

1. +=  O(n^2)
不过可以优化

2. 使用列表存储分片,然后最后使用`''.join(list)`方法组合起来.  O(n)

3. 列表解析式(生成器解析式)  最有效率
`letters = ''.join(c for c in document if c.isalpha())`
