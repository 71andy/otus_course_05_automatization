## web server (python3)

Задание в рамках обучения на курсе **Python Developer. Professional** (otus.ru)
Web сервер с использованием asyncio

#### Запуск сервера

```
python3 httpd.py [--root root_dir] [--workers workers_num] [--port port]
```

| Param   | Decsription                                                            |
| ------- | ---------------------------------------------------------------------- |
| workers | количество задач, обрабатывающих входящие подключения (по умолчанию 1) |
| root    | корневая папка контента веб-сервера (по умолчанию .)                   |
| port    | порт http сервера (по умолчанию 8080)                                  |

#### Запуск тестов

```
python3 httptest.py
```

#### Нагрузочноге тестирование

Тестирование выполнялось в докер-контейнере, собранном на базе _python:3.9.7-slim-buster_

```
ab -n 50000 -c 100 -r http://127.0.0.1:8080/
```

Результаты

```
Server Software:        Otus
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /
Document Length:        14 bytes

Concurrency Level:      100
Time taken for tests:   27.113 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      8700000 bytes
HTML transferred:       700000 bytes
Requests per second:    1844.12 [#/sec] (mean)
Time per request:       54.226 [ms] (mean)
Time per request:       0.542 [ms] (mean, across all concurrent requests)
Transfer rate:          313.36 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    5   3.4      4     105
Processing:    -4   49  16.5     47     243
Waiting:        0   41  15.3     40     240
Total:          0   54  16.5     52     252

Percentage of the requests served within a certain time (ms)
  50%     52
  66%     56
  75%     58
  80%     60
  90%     67
  95%     76
  98%    100
  99%    120
 100%    252 (longest request)
```
