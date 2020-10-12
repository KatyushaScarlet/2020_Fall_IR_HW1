WARC Indexer
============
# Usage
`python3 main.py filename [-cf] [-sw] [-st]`

# Parameters:
1. -cf use case folding
2. -sw use stopword removal
3. -st use stemming

# Input example:
`python3 main.py 01.warc.gz -cf -sw -st`

or

`python3 main.py 01.warc -cf -sw -st`

# Output example:
1. 01.warc.gz.index.dict (dictionary)
2. 01.warc.gz.index.idx (inverted index)
3. Console Output
```
Start......
----------------------------------------------------------
Analysis document:
48.47459816932678 s
Average: 1.7060110568496791 ms
Document process per second: 586.1626722669668 ps
----------------------------------------------------------
build full index ......
----------------------------------------------------------
Build full index:
18.97804856300354 s
Average: 0.6679118942423995 ms
DPS: 1497.203461444989 ps
----------------------------------------------------------
dump index from memory to file
----------------------------------------------------------
dump index:
13.609108209609985 s
----------------------------------------------------------
finish
----------------------------------------------------------
Total time analysis:
81.0864520072937 s
Average 2.8537500749594593 ms
DPS 350.41606563296597 ps
```

