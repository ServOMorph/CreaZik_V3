Set-Location D:\ServOMorph\CreaZik_V3\webradio
foreach ($i in 1..3) {
    python generate.py tests_ace/funky_yogi/config.json --only $i *> "tests_ace/funky_yogi/gen_v$i.log"
}
"FIN" | Out-File tests_ace/funky_yogi/fin.txt
