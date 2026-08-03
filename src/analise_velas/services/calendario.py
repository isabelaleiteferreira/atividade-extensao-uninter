# datas que fazem vender mais vela (feriados, dias de santo, etc)
from datetime import date

MESES = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",
         7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

# lista das datas fixas do ano
DATAS = [
    {"nome":"Ano Novo", "mes":1, "forte":False},
    {"nome":"Dia de Iemanja", "mes":2, "forte":True},
    {"nome":"Dia de Sao Jorge", "mes":4, "forte":False},
    {"nome":"Dia das Maes", "mes":5, "forte":False},
    {"nome":"Dia de Santo Antonio", "mes":6, "forte":False},
    {"nome":"Dia de Sao Joao", "mes":6, "forte":False},
    {"nome":"Cosme e Damiao", "mes":9, "forte":False},
    {"nome":"Nossa Senhora Aparecida", "mes":10, "forte":True},
    {"nome":"Finados", "mes":11, "forte":True},
    {"nome":"Natal", "mes":12, "forte":False},
]


def calcular_pascoa(ano):
    # formula pronta da internet pra achar a pascoa (ela muda todo ano)
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    x = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*x) // 451
    mes = (h + x - 7*m + 114) // 31
    dia = ((h + x - 7*m + 114) % 31) + 1
    return date(ano, mes, dia)


def datas_do_mes(mes, ano):
    # pega as datas daquele mes
    lista = [d for d in DATAS if d["mes"] == mes]
    # a semana santa muda de mes todo ano, por isso e calculada separado
    if mes == calcular_pascoa(ano).month:
        lista.append({"nome": "Semana Santa", "mes": mes, "forte": True})
    return lista
