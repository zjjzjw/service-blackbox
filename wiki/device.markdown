### Introduction

    1.set some options to device

    2.get all controllers registered from mysql database

    3.create all workers with controller name

    4.register SIGHUP signal with a function

    5.loop to recieve msg and pub it

    6.in loop maintain if workers are live every second by default 


### Signal to handler

    1. SIGHUP 1 reload all controller from mysql 

    2. SIGINT 2 quit device and all workers

    3. SIGUSR1 10 outpur version info and workers' info
