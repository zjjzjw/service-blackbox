#### MQ structure
```
              +------+          +------+          +------+
              |Client|          |Client|          |Client|
              +------+          +------+          +------+
              | PUSH |          | PUSH |          | PUSH |
              +--+---+          +--+---+          +--+---+
                 |                 |                 |
                 +-----------------+-----------------+
                                   |
                               +---+----+
                               |  PULL  |
                               +--------+
                               | Agent  |
                               +---+----+
                               |PUB|PULL|
                               +-+-+--+-+
                                 |    |
                                 |    +----------------+
                +----------------+----------------+    |
                |                |                |    |
              +-+-+--+-+       +-+-+--+-+       +-+-+--+-+
              |SUB|PUSH|       |SUB|PUSH|       |SUB|PUSH|
              +---+----+       +---+----+       +---+----+
              | Worker |       | Worker |       | Worker |
              +--------+       +--------+       +--------+
```

#### RELOAD
    * Frame 1: "v1"
    * Frame 2: 0x04
    * Frame 3: Timestamp (msgpacked)
    * Frame 4: EMPTY
    * Frame 5: Request data(reload)

#### HEARTBEAT
    * Frame 1: "v1"
    * Frame 2: 0x03 (one byte, representing HEARTBEAT)
    * Frame 3: Timestamp (msgpacked)
    * Frame 4: EMPTY
    * Frame 5: Request data(controller_name->msgpacked)

#### GOODBY
    * Frame 1: page_id-controller_name
    * Frame 2: "v1"
    * Frame 3: 0x02 (one byte, representing GOODBYE)
    * Frame 4: Timestamp (msgpacked)
    * Frame 5: EMPTY

#### REQUEST
    * Frame 1: page_id-controller_name
    * Frame 2: "v1"
    * Frame 3: 0x00 (one byte, representing PUB REQUEST)
    * Frame 4: Timestamp (msgpacked)
    * Frame 5: Empty
    * Frame 6: Request data (msgpacked)

#### CLIENT
    * Frame 1: "v1"
    * Frame 2: 0x00 (one byte, representing CLIENT PUSH)
    * Frame 3: Timestamp (msgpacked)
    * Frame 4: Empty
    * Frame 5: Request data (msgpacked)

#### Request data (json)
    {
        "controller_name":"recomment",
        "app_name":"app10-006",
        "execution_time":182,
        "module_time":{"mysql":79, "memcache":53},
        "frame_time":{"controller":55, "page":60, "component":32},
        "url":"shanghai.anjuke.com",
        "user_defined":{"Get A":38, "Get B":18, "Get C":23},
        "sql_count":50      
    }
