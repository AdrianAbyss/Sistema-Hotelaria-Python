import json
from pathlib import Path
from datetime import datetime

ARQUIVO = Path("dados_em_json.json")

LIVRE = "LIVRE"
OCUPADO = "OCUPADO"
MANUTENCAO = "MANUTENÇÃO"
TIPOS_QUARTO = ("solitario", "duo")

dados = {
    "quartos": [],
    "clientes": [],
    "reservas": [],
    "proximos": {"quarto": 1, "cliente": 1, "reserva": 1},
}


#storage
def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)


def carregar():
    global dados
    if not ARQUIVO.exists():  # primeira execução: mantém o dicionário vazio
        return
    with open(ARQUIVO, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)


# entrada
def ler_int(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro válido.")


def ler_float(mensagem):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))
        except ValueError:
            print("Digite um valor numérico válido.")
            continue
        if valor <= 0:
            print("O valor deve ser maior que zero.")
            continue
        return valor


def ler_data(mensagem):
    while True:
        try:
            return datetime.strptime(input(mensagem), "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida. Use dia/mês/ano, ex: 25/12/2026.")


def buscar_por_id(lista, id_procurado):
    for item in lista:
        if item["id"] == id_procurado:
            return item
    return None


# cadastros
def cadastro_dos_quartos():
    numero = ler_int("Digite o número do quarto: ")
    if any(q["numero"] == numero for q in dados["quartos"]):
        print("Já existe um quarto com esse número.")
        return

    while True:
        tipo = input("Tipo do quarto (solitario/duo): ").strip().lower()
        if tipo in TIPOS_QUARTO:
            break
        print("Tipo inválido. Digite 'solitario' ou 'duo'.")

    valor = ler_float("Valor da diária do quarto: ")

    while True:
        opcao = input("Condição do quarto (1 - Livre / 2 - Manutenção): ").strip()
        if opcao == "1":
            estado = LIVRE
            break
        if opcao == "2":
            estado = MANUTENCAO
            break
        print("Opção inválida.")

    dados["quartos"].append({
        "id": dados["proximos"]["quarto"],
        "numero": numero,
        "tipo": tipo,
        "valor_da_diaria": valor,
        "estado": estado,
    })
    dados["proximos"]["quarto"] += 1
    salvar()
    print("Quarto cadastrado.")


def cadastro_dos_clientes():
    nome = input("Digite o nome do cliente: ").strip()
    if not nome:
        print("O nome não pode ficar vazio.")
        return

    cpf = input("Digite o CPF do cliente (11 dígitos): ").replace(".", "").replace("-", "").strip()
    if len(cpf) != 11 or not cpf.isdigit():
        print("CPF inválido. Digite 11 números.")
        return
    if any(c["cpf"] == cpf for c in dados["clientes"]):
        print("Já existe um cliente com esse CPF.")
        return

    dados["clientes"].append({
        "id": dados["proximos"]["cliente"],
        "nome": nome,
        "cpf": cpf,
    })
    dados["proximos"]["cliente"] += 1
    salvar()
    print("Cliente cadastrado.")


#listagem
def ver_quartos():
    if not dados["quartos"]:
        print("Nenhum quarto cadastrado.")
        return
    for q in dados["quartos"]:
        print(f"  ID: {q['id']} | Nº {q['numero']} | {q['tipo']} | "
              f"R${q['valor_da_diaria']:.2f} | {q['estado']}")


def ver_clientes():
    if not dados["clientes"]:
        print("Nenhum cliente cadastrado.")
        return
    for c in dados["clientes"]:
        print(f"  ID: {c['id']} | Nome: {c['nome']} | CPF: {c['cpf']}")


#check in
def check_in():
    id_cliente = ler_int("Digite o ID do cliente: ")
    id_quarto = ler_int("Digite o ID do quarto: ")

    cliente = buscar_por_id(dados["clientes"], id_cliente)
    quarto = buscar_por_id(dados["quartos"], id_quarto)
    if cliente is None or quarto is None:
        print("Cliente ou quarto não encontrado.")
        return

    #regra pra so aceitar checkin em quarto livrea
    if quarto["estado"] != LIVRE:
        print(f"Quarto indisponível (estado: {quarto['estado']}). "
              "Só quartos LIVRES aceitam check-in.")
        return

    data_entrada = ler_data("Digite a data de entrada (dia/mês/ano): ")
    data_saida = ler_data("Digite a data de saída prevista (dia/mês/ano): ")
    if data_saida <= data_entrada:
        print("A data de saída deve ser depois da data de entrada.")
        return

    dados["reservas"].append({
        "id": dados["proximos"]["reserva"],
        "id_cliente": id_cliente,
        "id_quarto": id_quarto,
        "data_entrada": data_entrada.isoformat(),
        "data_saida_prevista": data_saida.isoformat(),
        "status": "ATIVA",
    })
    dados["proximos"]["reserva"] += 1
    quarto["estado"] = OCUPADO
    salvar()

    diarias = (data_saida - data_entrada).days  # diárias = saída - chegada
    total = diarias * quarto["valor_da_diaria"]  # total = diárias x valor
    print(f"Check-in realizado para {cliente['nome']} no quarto {quarto['numero']}.")
    print(f"Previsão: {diarias} diária(s), total de R${total:.2f}.")


#check out
def check_out():
    id_reserva = ler_int("Digite o ID da reserva: ")
    reserva = buscar_por_id(dados["reservas"], id_reserva)
    if reserva is None:
        print("Reserva não encontrada.")
        return

    quarto = buscar_por_id(dados["quartos"], reserva["id_quarto"])
    if quarto is None:
        print("Quarto da reserva não encontrado.")
        return

    if reserva["status"] != "ATIVA":
        print("Reserva já finalizada.")
        return

    data_saida_real = ler_data("Digite a data de saída real (dia/mês/ano): ")
    data_entrada = datetime.fromisoformat(reserva["data_entrada"]).date()
    if data_saida_real < data_entrada:
        print("A data de saída real não pode ser antes da entrada.")
        return

    diarias = (data_saida_real - data_entrada).days
    total = diarias * quarto["valor_da_diaria"]

    reserva["status"] = "FINALIZADA"
    quarto["estado"] = LIVRE
    salvar()

    print(f"Check-out realizado. Total de {diarias} diária(s), valor total R${total:.2f}.")


#relatório de reservas
def relatorio_de_reservas():
    if not dados["reservas"]:
        print("Nenhuma reserva registrada.")
        return

    for r in dados["reservas"]:
        cliente = buscar_por_id(dados["clientes"], r["id_cliente"])
        quarto = buscar_por_id(dados["quartos"], r["id_quarto"])

        nome_cliente = cliente["nome"] if cliente is not None else "Cliente não encontrado"
        numero_quarto = quarto["numero"] if quarto is not None else "Quarto não encontrado"

        print(f"Reserva ID: {r['id']} | Cliente: {nome_cliente} | "
              f"Quarto Nº {numero_quarto} | Entrada: {r['data_entrada']} | "
              f"Saída Prevista: {r['data_saida_prevista']} | Status: {r['status']}")

#interface
def menu():
    carregar()
    while True:
        print("\n1 - cadastro de quartos")
        print("2 - listagem de quartos")
        print("3 - cadastro de clientes")
        print("4 - listagem de clientes")
        print("5 - check-in")
        print("6 - check-out")
        print("7 - relatório de reservas")
        print("0 - sair")
        escolha = input("Digite a opção desejada: ").strip()

        match escolha:
            case "1":
                cadastro_dos_quartos()
            case "2":
                ver_quartos()
            case "3":
                cadastro_dos_clientes()
            case "4":
                ver_clientes()
            case "5":
                check_in()
            case "6":
                check_out()
            case "7":
                relatorio_de_reservas()
            case "0":
                print("Encerrando o sistema.")
                break
            case _:
                print("Opção inválida.")


if __name__ == "__main__":
    menu()