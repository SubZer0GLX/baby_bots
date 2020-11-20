from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
from colorama import init, Fore, Back
from time import time
import getpass
import sys, os
import webbrowser
import telebot
import subprocess
from flask import Flask, request
init(convert=True, autoreset=True)
#bot = telebot.TeleBot("1430084923:AAHSAoCdwrR8Zv2YjM7HL56FPnY-QgBAKlE")

TOKEN = '1430084923:AAHSAoCdwrR8Zv2YjM7HL56FPnY-QgBAKlE'
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)

#email = input('\n Email da IqOption: ')
#senha = getpass.getpass('\n Senha: ')
API = IQ_Option('marcosviniciuotto@gmail.com', 'e91664192a')
API.connect()

if API.check_connect():
	print(Fore.LIGHTGREEN_EX + '\n Conectado com sucesso!')
else:
	print(Fore.LIGHTRED_EX + ' Erro ao conectar')
	input('\n Aperte enter para sair')
	sys.exit()
print(Fore.LIGHTCYAN_EX + '''
______________________________________________________________________________
______   ___  ______ __   __         _____  _____  _   _   ___   _____  _____  
| ___ \ / _ \ | ___ \\ \ / /        /  ___||_   _|| \ | | / _ \ |_   _|/  ___| 
| |_/ // /_\ \| |_/ / \ V /  ______ \ `--.   | |  |  \| |/ /_\ \  | |  \ `--.  
| ___ \|  _  || ___ \  \ /  |______| `--. \  | |  | . ` ||  _  |  | |   `--. \ 
| |_/ /| | | || |_/ /  | |          /\__/ / _| |_ | |\  || | | | _| |_ /\__/ / 
\____/ \_| |_/\____/   \_/          \____/  \___/ \_| \_/\_| |_/ \___/ \____/  
                                                                               
        Creditos ao canal iqcoding >> https://www.youtube.com/c/IQCoding                                                                                                               
______________________________________________________________________________                                                   
''')

def cataloga(par, dias, prct_call, prct_put, timeframe):
	data = []
	datas_testadas = []
	time_ = time()
	sair = False
	while sair == False:
		velas = API.get_candles(par, (timeframe * 60), 1000, time_)
		velas.reverse()
		
		for x in velas:	
			if datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d') not in datas_testadas: 
				datas_testadas.append(datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d'))
				
			if len(datas_testadas) <= dias:
				x.update({'cor': 'verde' if x['open'] < x['close'] else 'vermelha' if x['open'] > x['close'] else 'doji'})
				data.append(x)
			else:
				sair = True
				break
				
		time_ = int(velas[-1]['from'] - 1)

	analise = {}
	for velas in data:
		horario = datetime.fromtimestamp(velas['from']).strftime('%H:%M')
		if horario not in analise : analise.update({horario: {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0, 'dir': ''}})	
		analise[horario][velas['cor']] += 1
		
		try:
			analise[horario]['%'] = round(100 * (analise[horario]['verde'] / (analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])))
		except:
			pass
	
	for horario in analise:
		if analise[horario]['%'] > 50 : analise[horario]['dir'] = 'CALL'
		if analise[horario]['%'] < 50 : analise[horario]['%'],analise[horario]['dir'] = 100 - analise[horario]['%'],'PUT '
	
	return analise
global timeframe, dias, porcentagem, martingale, mercado
#print(Fore.LIGHTWHITE_EX + '\n\n Qual timeframe deseja analisar?: ', end='')
timeframe = 15#int(input())

#print(Fore.LIGHTWHITE_EX + '\n Quantos dias deseja analisar?: ', end='')
dias = 10#int(input())

#print(Fore.LIGHTWHITE_EX + '\n Porcentagem minima?: ', end='')
porcentagem = 80#int(input())

#print(Fore.LIGHTWHITE_EX + '\n Quantos Martingales?: ', end='')
martingale = int(2)#input()

#print(Fore.LIGHTWHITE_EX + '\n Catalogar mercado normal ou otc?: ', end='')
mercado = 'OTC'#input().upper()

def Cat(timeframe, dias, porcentagem, martingale, mercado):
	prct_call = abs(porcentagem)
	prct_put = abs(100 - porcentagem)

	P = API.get_all_open_time()

	print('\n\n')
	actives_otc = ['GBPJPY-OTC', 'EURUSD-OTC', 'EURGBP-OTC', 'USDCHF-OTC', 'EURJPY-OTC', 'NZDUSD-OTC', 'GBPUSD-OTC', 'USDJPY-OTC', 'AUDCAD-OTC']
	actives = ['EURUSD','EURGBP', 'GBPJPY', 'EURJPY', 'GBPUSD', 'USDJPY', 'AUDCAD', 'NZDUSD', 'USDCHF', 'AUDUSD', 'USDCAD', 'AUDJPY', 'GBPCAD', 'GBPCHF', 'GBPAUD', 'EURCAD', 'CHFJPY', 'CADCHF', 'EURAUD', 'EURNZD', 'AUDCHF', 'AUDNZD', 'CADJPY', 'EURCHF', 'GBPNZD', 'NZDCAD', 'NZDJPY']
	catalogacao = {}
	try:
		ativos = actives_otc if mercado == 'OTC' else actives
		for par in ativos:
			timer = int(time())
			print(Fore.GREEN + '*' + Fore.RESET + ' CATALOGANDO - ' + par + '.. ', end='')
			
			catalogacao.update({par: cataloga(par, dias, prct_call, prct_put, timeframe)})	
			
			for par in catalogacao:
				for horario in sorted(catalogacao[par]):
					if martingale != '':					
					
						mg_time = horario
						soma = {'verde': catalogacao[par][horario]['verde'], 'vermelha': catalogacao[par][horario]['vermelha'], 'doji': catalogacao[par][horario]['doji']}
						
						for i in range(int(martingale)):

							catalogacao[par][horario].update({'mg'+str(i+1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0} })

							mg_time = str(datetime.strptime((datetime.now()).strftime('%Y-%m-%d ') + str(mg_time), '%Y-%m-%d %H:%M') + timedelta(minutes=timeframe))[11:-3]
							
							if mg_time in catalogacao[par]:
								catalogacao[par][horario]['mg'+str(i+1)]['verde'] += catalogacao[par][mg_time]['verde'] + soma['verde']
								catalogacao[par][horario]['mg'+str(i+1)]['vermelha'] += catalogacao[par][mg_time]['vermelha'] + soma['vermelha']
								catalogacao[par][horario]['mg'+str(i+1)]['doji'] += catalogacao[par][mg_time]['doji'] + soma['doji']
								
								catalogacao[par][horario]['mg'+str(i+1)]['%'] = round(100 * (catalogacao[par][horario]['mg'+str(i+1)]['verde' if catalogacao[par][horario]['dir'] == 'CALL' else 'vermelha'] / (catalogacao[par][horario]['mg'+str(i+1)]['verde'] + catalogacao[par][horario]['mg'+str(i+1)]['vermelha'] + catalogacao[par][horario]['mg'+str(i+1)]['doji']) ) )
								
								soma['verde'] += catalogacao[par][mg_time]['verde']
								soma['vermelha'] += catalogacao[par][mg_time]['vermelha']
								soma['doji'] += catalogacao[par][mg_time]['doji']
							else:						
								catalogacao[par][horario]['mg'+str(i+1)]['%'] = 'N/A'
			
			print('finalizado em ' + str(int(time()) - timer) + ' segundos')

		print('\n\n')

		for par in catalogacao:
			for horario in sorted(catalogacao[par]):
				ok = False		
				
				if catalogacao[par][horario]['%'] >= porcentagem:
					ok = True
				else:
					for i in range(int(martingale)):
						if catalogacao[par][horario]['mg'+str(i+1)]['%'] >= porcentagem:
							ok = True
							break
				
				if ok == True:
				
					msg = Fore.YELLOW + par + Fore.RESET + ' - ' + horario + ' - ' + (Fore.RED if catalogacao[par][horario]['dir'] == 'PUT ' else Fore.GREEN) + catalogacao[par][horario]['dir'] + Fore.RESET + ' - ' + str(catalogacao[par][horario]['%']) + '% - ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['verde']) + Back.RED + Fore.BLACK + str(catalogacao[par][horario]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['doji'])
					
					if martingale != '':
						for i in range(int(martingale)):
							if str(catalogacao[par][horario]['mg'+str(i+1)]['%']) != 'N/A':
								msg += ' | MG ' + str(i+1) + ' - ' + str(catalogacao[par][horario]['mg'+str(i+1)]['%']) + '% - ' + Back.GREEN + Fore.BLACK + str(catalogacao[par][horario]['mg'+str(i+1)]['verde']) + Back.RED + Fore.BLACK + str(catalogacao[par][horario]['mg'+str(i+1)]['vermelha']) + Back.RESET + Fore.RESET + str(catalogacao[par][horario]['mg'+str(i+1)]['doji'])
							else:
								msg += ' | MG ' + str(i+1) + ' - N/A - N/A' 
								
					print(msg)	
					open('C:/Users/babytrader/Desktop/bot_telegram/sinais.txt', 'a').write('M'+ str(timeframe) + ';' + par + ';' + horario + ':00;' + catalogacao[par][horario]['dir'].strip() + '\n')
	except:
		print()
"""os.remove("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt")
Cat(timeframe, dias, porcentagem, martingale, mercado)
x = open('C:/Users/babytrader/Desktop/bot_telegram/sinais.txt')
y = []
for i in x.readlines():
	y.append(i)
y.sort(key=lambda item: datetime.strptime(item.split(";")[2], "%H:%M:%S"))
x.close
str1 = ''.join(str(e) for e in y)
print(str1)"""
def reabrirbot():
	command = "catalgador.py"
	subprocess.Popen(command)

def cata():
	x = open('C:/Users/babytrader/Desktop/bot_telegram/sinais.txt')
	y = []
	for i in x.readlines():
		y.append(i)
	y.sort(key=lambda item: datetime.strptime(item.split(";")[2], "%H:%M:%S"))
	x.close
	places = y
	with open('C:/Users/babytrader/Desktop/bot_telegram/sinais.txt', 'w') as filehandle:
		for listitem in places:
			filehandle.write('%s' % listitem)

fila = 0
@bot.message_handler(commands=['status'])
def status(session):
	bot.reply_to(session, '🤖 Estou funcionando ')
	#os.execv(sys.executable, ['python'] + sys.argv)
@bot.message_handler(commands=['lista'])
def add_sinal(session):
	global fila, timeframe, dias, porcentagem, martingale, mercado
	chat = '-1001462190248'
	my = session.from_user.username
	print(my)
	compl = session.from_user
	cid = session.chat.id
	sg = str(session.text)
	usario = '@' + str(my)
	print(cid, sg, compl)
	#bot.delete_message(session, cid)
	if str(cid) == chat:
		if fila == 0:
			msgid = 0
			fila = 1
			if os.path.exists("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt"):
				os.remove("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt")
			else:
				print("The file does not exist")
			entra = True
			try:
				#bot.reply_to(session, 'Iniciando catalogação .....\nPor favor não execute comandos até finalizar a catalogação')
				msg = str(session.text).split()
				timeframe = int(msg[1])
				dias = int(msg[2])
				if timeframe == 1 and dias > 30:
					entra = False
					fila = 0
					bot.reply_to(session, 'Para M1 use menos de 30 dias 🔽')
				elif timeframe == 5 and dias > 50:
					entra = False
					fila = 0
					bot.reply_to(session, 'Para M5 use menos de 50 dias 🔽')
				porcentagem = int(msg[3])
				martingale = int(msg[4])
				mercado = str(msg[5]).upper()
			except:
				entra = False
				fila = 0
				bot.reply_to(session, 'Formato incorreto ❗')
				os.execv(sys.executable, ['python'] + sys.argv)
				
			if entra:
				bot.reply_to(session, 'Iniciando catalogação, espere finalizar ⏳')
				try:
					Cat(timeframe, dias, porcentagem, martingale, mercado)
				except:
					print()
				fila = 0
				try:
					if os.path.exists("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt"):
						cata()
						#do = open("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt", "r")
						#data = do.read()
						#bot.reply_to(session,data)
						dat = '📊 M'+str(timeframe)+str(datetime.now().strftime(' %d/%m/%Y '))+str(usario)
						doc = open("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt", "r")
						bot.send_document(chat, doc, caption=dat)
						file_id = str(cid)
						#bot.reply_to(session, usario)
						#bot.reply_to(session,sg)
						bot.send_document(chat, file_id, caption=dat)
						fila = 0
						
					else:
						bot.reply_to(session, str(sg) + ' Não encontrado sinais para essa configuração ⭕')
					fila = 0
				except:
					print()
					cata()
					if os.path.exists("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt"):
						print()
						"""dat = '📊 M'+str(timeframe)+str(datetime.now().strftime(' %d/%m/%Y '))+str(usario)
						doc = open("C:/Users/babytrader/Desktop/bot_telegram/sinais.txt", "r")
						bot.send_document(chat, doc, caption=dat)
						file_id = str(cid)
						bot.send_document(chat, file_id, caption=dat)"""
					else:
						bot.reply_to(session, str(sg) + ' Não encontrado sinais para essa configuração ⭕')
					os.execv(sys.executable, ['python'] + sys.argv)
					#reabrirbot()
		else:
			bot.reply_to(session, 'Aguarde finalizar a catalogação recorrente 🔃')
	else:
		bot.reply_to(session, '❌ Apenas grupo @Baby_Sinais tem permisão para usar o bot ❌')
cont = 0

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
   bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
   return "!", 200
@server.route("/")
def webhook():
   bot.remove_webhook()
   bot.set_webhook(url='https://vast-harbor-68092.herokuapp.com/' + TOKEN)
   return "!", 200
if __name__ == "__main__":
   server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
	