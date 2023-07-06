# sdxl-scrum
sdxl training RTA




## 数据收集:

1. 获取推特关注: repo: twitter-suite -> floowing.json
2. 推特关注转danbooru: danbooru_handle_getter.py

(众包收集: send_req.py)

## 筛选:

**twitter账号:**

如果关注 > 10000:
- 如果没有任意一张图like > 1000: 丢弃
- 丢弃所有 < 150 like的图

如果关注> 1000:
- 如果没有任意一张图like > 500: 丢弃
- 丢弃所有 < 50 like的图

如果关注 < 1000:
- 如果没有任意一张图like > 100: 丢弃
- 丢弃所有 < 10 like的图

对于所有关注<1000的账号:
- 如果没有任意一张图like > 500: 输出到likely_not.json, 手动筛选


twitter post: