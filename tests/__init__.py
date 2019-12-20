"""
https://fastapi.tiangolo.com/tutorial/testing/
https://docs.python.org/3.7/library/asyncio-task.html

First, run a simple `pytest - x` to get closer to an error
```
pytest - x
```

Second, run with coverage
```
pytest  --cov=src --cov-branch -x -vv
```

An HTML report highlighting potentially uncovered
application code can be created after a successful run:
```
coverage html
```

on a desktop machine
```
firefox htmlcov/index.html
```

build a new docker images
```
docker run -p 5000:5000 --restart unless-stopped -d fast-api:slim-nonroot
```


Tests should be repeated with an built docker image.
However, since that is a part of deployment it is deferred or skipped completely.
But at, least check, whether the image can be run as container:
```
docker run -p 5000:5000 --restart unless-stopped -d fast-api:slim-nonroot
```

```
git push origin master
```

```
git pull origin master
```


"""

