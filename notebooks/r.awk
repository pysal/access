
FNR == 1 { file+=1 }

file == 1 { ORIGINS[$1]=1 ; next } 

file == 2 { DESTINATIONS[$1]=1 ; next } 

($1 in ORIGINS) && ($2 in DESTINATIONS)

