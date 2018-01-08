<?php
$context = new ZMQContext();
$sender = new ZMQSocket($context, ZMQ::SOCKET_PUSH);
$sender->connect("tcp://127.0.0.1:7555");

function create_info_1(){
     $info = array(
        "controller_name" => "Listing_Property_Sales",
        "app_name" => "app11-00".rand(1,3),
        "execution_time" => rand(80,220),
        "module_time" => array(
            "mysql" => rand(30,70),
            "memcache" => rand(20,50),
        ),
        "frame_time" => array(
            "controller" => rand(30,150),
            "page" => rand(10,30),
            "component" => rand(35, 80)
        ),
        "url" => "shanghai.anjuke.com",
        "user_defined" => array(
            "A" => rand(20,75),
            "B" => rand(30,55),
            "C" => rand(80,12),
        )
    );
    return $info;
}

function create_info_2(){
     $info = array(
        "controller_name" => "Listing_Property_Sales",
        "app_name" => "app11-00".rand(1,3),
        "execution_time" => rand(180,320),
        "module_time" => array(
            "mysql" => rand(60,130),
            "memcache" => rand(45,90),
        ),
        "frame_time" => array(
            "controller" => rand(80,100),
            "page" => rand(40,60),
            "component" => rand(65, 100)
        ),
        "url" => "shanghai.anjuke.com",
        "user_defined" => array(
            "A" => rand(60,115),
            "B" => rand(60,55),
            "C" => rand(80,120),
        )
    );
    return $info;
}

while (True){
    for($i = 0; $i < 100; $i++){
        $info = create_info_1();
        $frames = array();
        $frames[] = 'v1';
        $frames[] = chr(0x00);
        $frames[] = msgpack_pack(round(microtime(true)*1000));
        $frames[] = '';
        $frames[] = msgpack_pack(json_encode($info));
        $last = array_pop($frames);
        foreach($frames as $frame){
            $sender->send($frame, ZMQ::MODE_SNDMORE);
        }
        $sender->send($last);

        sleep(1);
    }

    for($i = 0; $i < 100; $i++){
        $info = create_info_2();
        $frames = array();
        $frames[] = 'v1';
        $frames[] = chr(0x00);
        $frames[] = msgpack_pack(round(microtime(true)*1000));
        $frames[] = '';
        $frames[] = msgpack_pack(json_encode($info));
        $last = array_pop($frames);
        foreach($frames as $frame){
            $sender->send($frame, ZMQ::MODE_SNDMORE);
        }
        $sender->send($last);

        sleep(1);
    }
}
