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
Document Length:        330 bytes

Concurrency Level:      100
Time taken for tests:   48.188 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      24200000 bytes
HTML transferred:       16500000 bytes
Requests per second:    1037.60 [#/sec] (mean)
Time per request:       96.376 [ms] (mean)
Time per request:       0.964 [ms] (mean, across all concurrent requests)
Transfer rate:          490.43 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        1   46  14.5     43     212
Processing:     6   50  18.4     46     257
Waiting:        3   39  15.8     36     233
Total:         45   96  26.8     91     410

Percentage of the requests served within a certain time (ms)
  50%     91
  66%     98
  75%    104
  80%    108
  90%    122
  95%    140
  98%    174
  99%    212
 100%    410 (longest request)
```
