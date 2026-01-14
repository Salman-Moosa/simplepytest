#!/bin/bash 
Age=17
if [ "$Age" -ge 18 ]; then
    echo "youcan vote"
else
    echo "u cant dude";
fi        

for i in 1 2 3
do
  echo $i
done

i=1
while [ $i -le 3 ]
do
  echo $i
  i=$((i+1))
done

for i in 1 2 3 4
do
  if [ $i -eq 3 ]; then
    break
  fi
  echo $i
done

for i in 1 2 3 4
do
  if [ $i -eq 3 ]; then
    continue
    echo "u have not printed 3"
  fi
  echo $i
done
