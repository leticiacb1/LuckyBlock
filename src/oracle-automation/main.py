import requests

def obter_dados_megasena(id_concurso: int | None) -> dict | None:
    """
    Busca os dados de um concurso da Mega Sena na API da Caixa.

    Args:
        id_concurso: O número do concurso a ser pesquisado.

    Returns:
        Um dicionário com as chaves 'acumulado', 'dataApuracao',
        'dataProximoConcurso' e 'dezenasSorteadasOrdemSorteio'
        se a requisição for bem-sucedida (status 200).
        Retorna None caso contrário.
    """

    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{id_concurso if id_concurso else ''}" ## request com id vazio busca o último concurso
    try:
        response = requests.get(url, verify=False) # verify=False é geralmente usado para ambientes de teste ou URLs sem certificado SSL válido. Para produção, o ideal é ter o certificado correto.

        if response.status_code == 200:
            dados_json = response.json()
            chaves_interesse = [
                "acumulado",
                "dataApuracao",
                "dataProximoConcurso",
                "dezenasSorteadasOrdemSorteio"
            ]
            resultado = {chave: dados_json.get(chave) for chave in chaves_interesse}
            return resultado
        else:
            print(f"Erro ao buscar dados. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    except ValueError as e: # Captura erros de decodificação JSON
        print(f"Erro ao decodificar JSON: {e}")
        print(f"Conteúdo da resposta: {response.text[:200]}...") # Mostra parte do conteúdo problemático
        return None

if __name__ == '__main__':
    id_exemplo = 2868 # Substitua por um ID de concurso válido se necessário
    dados_concurso = obter_dados_megasena(id_exemplo)

    if dados_concurso:
        print(f"\n--- Dados do Concurso {id_exemplo} ---")
        print(f"Acumulado: {dados_concurso.get('acumulado')}")
        print(f"Data da Apuração: {dados_concurso.get('dataApuracao')}")
        print(f"Data do Próximo Concurso: {dados_concurso.get('dataProximoConcurso')}")
        print(f"Dezenas Sorteadas: {dados_concurso.get('dezenasSorteadasOrdemSorteio')}")
    else:
        print(f"Não foi possível obter os dados para o concurso {id_exemplo}.")

    # Exemplo com um ID que pode não existir ou ser inválido
    id_invalido = 0
    print(f"\n--- Tentando buscar concurso inválido: {id_invalido} ---")
    dados_concurso_invalido = obter_dados_megasena(id_invalido)
    if not dados_concurso_invalido:
        print(f"Falha ao buscar dados para o concurso {id_invalido}, como esperado.")