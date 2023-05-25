#!/usr/bin/env python3

# PAGE_SIZE = 262

# with open("redis-page.py", "w") as f:

#     f.write(f"import redis\n")
#     f.write(f"from redis import from_url\n")
#     f.write("redisClient = redis.from_url('redis://localhost:6379')\n\n")
#     for index in range(PAGE_SIZE):
#         f.write(f"redisClient.lpush('japan_figure:start_urls', 'https://japanfigure.vn/collections/all?page={index+1}')\n")
PAGE_SIZE = 80

with open("redis-page.py", "w") as f:

    f.write(f"import redis\n")
    f.write(f"from redis import from_url\n")
    f.write("redisClient = redis.from_url('redis://localhost:6379')\n\n")
    for index in range(PAGE_SIZE):
        f.write(f"redisClient.lpush('bucket_and_shovel:start_urls', 'https://bucketandshovel.com/collections/best-selling?page={index+1}')\n")
