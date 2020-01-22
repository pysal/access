
FNR == 1 { f+=1 }

f   == 1 { A[$1]=1 ; next } 

f   == 2 { B[$1]=1 ; next } 

($1 in A) && ($2 in B)

