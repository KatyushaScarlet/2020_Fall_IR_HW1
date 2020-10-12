WARC Indexer
============
#### 說明
1. 可以使用ClueWeb09_English_Sample.warc進行測試
2. 會產生

#### 使用方式
`python3 main.py filename [-cf] [-sw] [-st]`
##### Parameters:
1. -cf use case folding
2. -sw use stopword removal
3. -st use stemming

##### Input:
`python3 main.py 01.warc.gz -cf -sw -st`

or

`python3 main.py 01.warc -cf -sw -st`

##### Output
1. 產生 01.warc.gz.index.dict 的字典檔
2. 產生 01.warc.gz.index.idx 的 inverted index file
3. Sample Output
```
Start......
tmp/ewwMRMrTKfZGQQBdpxkh
----------------------------------------------------------
Analysis document:
48.97524404525757 s
Average: 1.7236307469999848 ms
Document process per second: 580.1706669137347 ps
----------------------------------------------------------
build full index ......
----------------------------------------------------------
Build full index:
18.96880793571472 s
Average: 0.6675866803587922 ms
DPS: 1497.932821940895 ps
----------------------------------------------------------
dump index from memory to file 01.warc.gz.index.txt
----------------------------------------------------------
dump index:
14.521172285079956 s
----------------------------------------------------------
finish
----------------------------------------------------------
Total time analysis:
82.49296188354492 s
Average 2.903250719246173 ms
DPS 344.44140116320295 ps
```

