def letter(n):
    if 64<n and n<91:
        return chr(n)
    else:
        return chr((n-65)//26+64)+letter((n-65)%26+65)


# left=ord(input("Left coord: "))-64
# top=int(input("Top coord: "))
# right=ord(input("Right coord: "))-64
# bot=int(input("Bottom coord: "))
# skip=int(input("Number of column to skip per iter: "))
# space=int(input("Space beetween tables: "))
# numb_table=int(input("Number of tables: "))

left=ord("B")
top=int(7)
right=ord("N")
bot=int(40)
skip=int(3)
space=int(1)
numb_table=int(11)

width=right-left
heigth=bot-top

FIRST_LINE=True
FIRST_COLUMN=True

#$Sheet1.$B$7:$B$40,$Sheet1.$D$7:$D$40,$Sheet1.$G$7:$G$40,$Sheet1.$J$7:$J$40,$Sheet1.$M$7:$M$40
for table in range(numb_table):
    print("\n"+str(table+1))
    for offset in range(1, skip+1):
        text="$Sheet1.${}${}:${}${}".format(letter(left), top, letter(left), bot)
        n1=left+offset+table*(width+space)
        for i in range(n1, n1+width, skip):
            text+=",$Sheet1.${}${}:${}${}".format(letter(i), top, letter(i), bot)
        print(text)
