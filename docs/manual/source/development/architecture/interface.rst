インターフェース
================

.. mermaid::

   flowchart TB
       event(event handler);
       m1[["MessageParser(MsgData)"]];

       event --> m1 --> d["dispatcher()"] --> f1 & f2 & f3;

       subgraph f1[Sub command]
           direction TB
           c([command]) --> sc1 & sc2 & sc3;
           sc1(summary) --> cp1[[CommandParser]] --> p1(aggregation);
           sc2(analysis) --> cp2[[CommandParser]] --> p2(aggregation);
           sc3(help) --> cp3[[CommandParser]] --> p3(text generation);
           p1 & p2 & p3 --> mp1[["MessageParser(PostData)<br>MessageParser(StatusData)"]];
       end

       subgraph f2[Results record]
           direction TB
           r2([record]);
           r2 --> a1(score) --> results[(results)];
           r2 --> a2(remark) --> remarks[(remarks)];
           results & remarks --> pp2["post_processing()"] --> mp2[["MessageParser(PostData)<br>MessageParser(StatusData)"]];
       end

       subgraph f3[Member management]
           direction TB
           r1([registry]);
           r1 --> a4(team) --> db2[(team)] & db1;
           r1 --> a3(member) --> db1[(member)] & db3[(alias)];
           r1 --> a5(alias) --> db3;
           db1 & db2 & db3  --> mp3[["MessageParser(PostData)<br>MessageParser(StatusData)"]];
       end

       f1 & f2 & f3 --> post["post()<br>(API Interface)"];

..
   ---
   config:
     flowchart:
       curve: linear
   ---
