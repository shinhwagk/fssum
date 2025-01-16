# fssum
```sh
curl -s https://cdn.jsdelivr.net/gh/shinhwagk/fssum/fssum.py -o /usr/bin/fssum
chmod +x fssum
```


```sh
rm -fr files.sum
find ./ -type f | while read line;do sum=`fssum "$line"`; echo "$sum $line" >> files.sum; done

cat files.sum  | awk '{print $1}' | sort | uniq -c | sort

cat files.sum | grep 603f91f2e9360ecb80eca9077eef71930c79d94e047b720f3a24f37e37276e64
```



```sh
python main.py --shasum-dir abc --shasum-file files.sumsha.json --shasum-force
```