# datas que fazem vender mais vela (feriados, dias de santo, etc)
from dateutil.easter import easter

MESES = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
         7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

# lista das datas fixas do ano
DATAS = [
    {"nome":"Ano Novo", "mes":1, "forte":False},
    {"nome":"Dia de Iemanjá", "mes":2, "forte":True},
    {"nome":"Dia de São Jorge", "mes":4, "forte":False},
    {"nome":"Dia das Mães", "mes":5, "forte":False},
    {"nome":"Dia de Santo Antônio", "mes":6, "forte":False},
    {"nome":"Dia de São João", "mes":6, "forte":False},
    {"nome":"Cosme e Damião", "mes":9, "forte":False},
    {"nome":"Nossa Senhora Aparecida", "mes":10, "forte":True},
    {"nome":"Finados", "mes":11, "forte":True},
    {"nome":"Natal", "mes":12, "forte":False},
]


def datas_do_mes(mes, ano):
    # pega as datas daquele mês
    lista = [d for d in DATAS if d["mes"] == mes]
    # a Páscoa muda de mês todo ano, por isso a Semana Santa é calculada à parte
    if mes == easter(ano).month:
        lista.append({"nome": "Semana Santa", "mes": mes, "forte": True})
    return lista
