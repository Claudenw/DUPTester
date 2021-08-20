rm -rf ./data.txt
touch data.txt
for((i=0;i<20000;i++))
do
str=',name';
name=${i}${str}${i}
echo  $name>> data.txt
done
