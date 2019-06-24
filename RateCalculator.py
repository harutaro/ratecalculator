#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#################################
# Rate Calculator version 0.0   #
# Author : @siro_live_0501      #
# Last modify : 2017/12/03      #
#################################
# teamgraph includes a bug when !miss is executed.
import discord
import os
import matplotlib.pyplot as plt
import pickle

client = discord.Client()
rate_dic = {} # レートを打ち込んだ人のIDと合計レート
tmp_rate_dic = {}
flag = False
save_path = os.path.expanduser('~/Desktop/RateCalc/save_data/')
save_path_local = os.path.expanduser('~/Desktop/RateCalc/save_rate/')
cmd_list = ['!c', '!miss', '!list', '!total', '!clear_all',\
            '!graph', '!graphall', '!restore', '!teamgraph']
ERR_CODE_NOT_INT = 11111111111
ERR_CODE_NAN     = 22222222222
manager = [xxxxxxxxxxxxxxxxxx] # permission for clear_all
sp = xxxxxxxxxxxxxxxxxx
teamrate = []

@client.event
async def on_ready():
    print("-"*20)
    print("ユーザ名：", client.user.name)
    print("ユーザID：", client.user.id)
    print("-"*20)

@client.event
async def on_message(message):
    global rate_dic
    global tmp_rate_dic
    global flag
    global cmd_list
    global ERR_CODE_NAN
    global ERR_CODE_NOT_INT
    global teamrate
    if not message.author.id == client.user.id:
        cmd = CommandExtract(message.content) # cmd extract
        try: # Unknown error occurs
            arg = ArgExtract(message.content)
        except: pass
        try:
            cmd[0] != '!'
        except: return -1
        if cmd[0] != '!': return -1
        if cmd == cmd_list[0]: # calculate !c
            if arg == ERR_CODE_NOT_INT:
                await client.send_message(message.channel,\
                                          'Argument must be integer')
                return -1
            elif arg == ERR_CODE_NAN:
                await client.send_message(message.channel,\
                                          'Usage:!c integer')
                return -1
            Calc_rate(message, arg)
            TeamRate(arg)
            with open(save_path_local + 'save.pickle', 'wb') as f:
                pickle.dump(rate_dic, f)
            l_t = str(Local_total(message))
            await client.send_message(message.channel, l_t)
        elif cmd == cmd_list[1]: # miss
            Miss(message)
            cmnt = 'Last Element is deleted'
            await client.send_message(message.channel, cmnt)
        elif cmd == cmd_list[2]: # list
            try:
                l_t = str(Local_total(message))
                await client.send_message(message.channel, l_t)
                num_vic, num_lose, ratio = Analyse(message)
                cmnt = str(num_vic) + '勝 ' + str(num_lose) + '敗 ' +\
                    '勝率: ' + str(ratio) + '\%'
                await client.send_message(message.channel, cmnt)
            except: pass
        elif cmd == cmd_list[3]: # total
            try:
                t_t, nv, nl, ratio = Team_Total()
                await client.send_message(message.channel,\
                                          'Team total = ' + str(t_t))
                cmnt = str(nv) + '勝 ' + str(nl) + '敗 ' +\
                    '勝率: ' + str(ratio) + '\%'
                await client.send_message(message.channel, cmnt)
            except: pass
        elif cmd == cmd_list[4]: # clear_all
            if not int(message.author.id) in manager:
                cmnt = 'You don\'t have permission for this command.'
                await client.send_message(message.channel, cmnt)
                return -1
            else:
                tmp_rate_dic = rate_dic
                rate_dic = {}
                teamrate = []
                flag = True
                await client.send_message(message.channel, 'Clear all rate')
        elif cmd == cmd_list[5]: # graph 
            CreateGraph(message)
            with open(save_path + 'foo.png', 'rb') as f:
                    await client.send_file(message.channel, f)
        elif cmd == cmd_list[6]: # graphall
            CreateGraphALL()
            with open(save_path + 'foo.png', 'rb') as f:
                    await client.send_file(message.channel, f)

        elif cmd ==  cmd_list[7]: # restore
            if int(message.author.id) != sp:
                cmnt = 'You don\'t have permission for this command.'
                await client.send_message(message.channel, cmnt)
                return -1
            else:
                with open(save_path_local + 'save.pickle', 'rb') as f:
                    rate_dic = pickle.load(f)
                await client.send_message(message.channel, 'Rate list is restored')
        elif cmd == cmd_list[8]: # teamgraph
            TeamGraph()
            with open(save_path + 'team.png', 'rb') as f:
                    await client.send_file(message.channel, f)
        elif cmd == cmd_list[9]:
            if arg == ERR_CODE_NOT_INT:
                await client.send_message(message.channel,\
                                          'Argument must be integer')
                return -1
            elif arg == ERR_CODE_NAN:
                await client.send_message(message.channel,\
                                          'Usage:!c integer')
                return -1
            Calc_rate(message, arg)
            TeamRate(arg)
# functions
def CommandExtract(message):
    return message.split(' ')[0]

def ArgExtract(message):
    message = message.replace('–', '-')
    message = message.replace('+', '')
    tmp = message.split(' ')
    if len(tmp) >= 2: # If !command integer
        if is_digit2(tmp[1]) == True:
            return tmp[1]
        else: return ERR_CODE_NOT_INT
    else: return ERR_CODE_NAN

def is_digit2(a_1): # 引数はString
    if a_1[0]=='-' and a_1[1:].isdigit() or a_1.isdigit():
        return True
    else:
        return False

def Calc_rate(message, arg):
    if not str(message.author.id) in rate_dic.keys():
        rate_dic[str(message.author.id)] = [int(arg)]
    else:
        rate_dic[str(message.author.id)].append(int(arg))

def Miss(message):
    if not str(message.author.id) in rate_dic.keys():
        return -1
    else:
        rate_dic[str(message.author.id)].pop()

def Analyse(message):
    num_vic = 0
    num_lose = 0
    for i in rate_dic[str(message.author.id)]:
        if i >= 0:
            num_vic += 1
        else:
            num_lose += 1
    return num_vic, num_lose, Victory_ratio(num_vic, num_lose)

def Victory_ratio(num_vic, num_lose):
    return round(100*float(num_vic)/(num_vic+num_lose), 3)

def Local_total(message):
    return sum(rate_dic[str(message.author.id)])

def Team_Total():
    total = 0
    num_vic = 0
    num_lose = 0
    for i in rate_dic.keys():
        for j in rate_dic[i]:
            if j >= 0:
                num_vic += 1
            else:
                num_lose += 1
        total += sum(rate_dic[i])
    return total, num_vic, num_lose, Victory_ratio(num_vic, num_lose)

def CreateGraph(message):
    yaxis = [0]
    tmp = 0
    for i in rate_dic[str(message.author.id)]:
        tmp += i
        yaxis.append(tmp)
    xaxis = range(len(yaxis))
    plt.xlabel("Number of games", fontsize=20, fontname='serif')
    plt.ylabel("Rate", fontsize=20, fontname='serif')
    plt.plot(xaxis, yaxis, '-D', color='#ff0000')
    plt.savefig(save_path + 'foo.png')
    plt.close()

def CreateGraphALL():
    col = ['red', 'blue', 'green', 'gray', \
           'purple', 'chocolate', 'black', 'navy', \
           'pink', 'aqua', 'yellow', 'tan', 'gold', 'silver',\
           'indigo']
    cnt = 0
    for i in rate_dic.values():
        yaxis = [0]
        tmp = 0
        for j in i:
            tmp += j
            yaxis.append(tmp)
        xaxis = range(len(yaxis))
        plt.xlabel("Number of games", fontsize=20, fontname='serif')
        plt.ylabel("Rate", fontsize=20, fontname='serif')
        plt.plot(xaxis, yaxis, '-D', color=col[cnt])
        plt.savefig(save_path + 'foo.png')
        cnt += 1
    plt.close()

def TeamRate(arg):
    teamrate.append(int(arg))

def TeamGraph():
    yaxis = [0]
    tmp = 0
    for i in teamrate:
        tmp += i
        yaxis.append(tmp)
    xaxis = range(len(yaxis))
    plt.xlabel("Number of games", fontsize=20, fontname='serif')
    plt.ylabel("Rate", fontsize=20, fontname='serif')
    plt.plot(xaxis, yaxis, '-D', color='#ff0000')
    plt.savefig(save_path + 'team.png')
    plt.close()

# main
client.run('Mzg2ODIyOTc5MjYwMTIxMDk4.DQVgiA.nB2-GlDmTbR4ZC59APunsX62wzM')
