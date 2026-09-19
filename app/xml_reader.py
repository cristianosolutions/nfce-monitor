import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime


NAMESPACE = {"nfe": "http://www.portalfiscal.inf.br/nfe"}


def buscar_texto(elemento, caminho, padrao=""):
    encontrado = elemento.find(caminho, NAMESPACE)

    if encontrado is not None and encontrado.text:
        return encontrado.text.strip()

    return padrao


def formatar_cnpj(cnpj):
    if not cnpj or len(cnpj) != 14:
        return cnpj

    return (
        f"{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/"
        f"{cnpj[8:12]}-{cnpj[12:14]}"
    )


def formatar_data(data_xml):
    if not data_xml:
        return ""

    try:
        data = datetime.fromisoformat(data_xml)
        return data.strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return data_xml


def definir_status(cstat):
    if cstat in ("100", "150"):
        return "AUTORIZADA"

    if cstat in ("101", "151"):
        return "CANCELADA"

    if cstat == "110":
        return "DENEGADA"

    if cstat:
        return "REJEITADA / OUTRO"

    return "SEM PROTOCOLO"


def ler_nfce(root, caminho):
    """
    Processa XML normal de NF-e/NFC-e.
    """

    inf_nfe = root.find(".//nfe:infNFe", NAMESPACE)

    if inf_nfe is None:
        return None

    chave = inf_nfe.get("Id", "").replace("NFe", "")

    numero = buscar_texto(
        inf_nfe,
        "nfe:ide/nfe:nNF"
    )

    serie = buscar_texto(
        inf_nfe,
        "nfe:ide/nfe:serie"
    )

    modelo = buscar_texto(
        inf_nfe,
        "nfe:ide/nfe:mod"
    )

    data_emissao = buscar_texto(
        inf_nfe,
        "nfe:ide/nfe:dhEmi"
    )

    cnpj = buscar_texto(
        inf_nfe,
        "nfe:emit/nfe:CNPJ"
    )

    emitente = buscar_texto(
        inf_nfe,
        "nfe:emit/nfe:xNome"
    )

    fantasia = buscar_texto(
        inf_nfe,
        "nfe:emit/nfe:xFant"
    )

    valor = buscar_texto(
        inf_nfe,
        "nfe:total/nfe:ICMSTot/nfe:vNF",
        "0.00"
    )

    protocolo = root.find(
        ".//nfe:infProt",
        NAMESPACE
    )

    if protocolo is not None:

        cstat = buscar_texto(
            protocolo,
            "nfe:cStat"
        )

        motivo = buscar_texto(
            protocolo,
            "nfe:xMotivo"
        )

        numero_protocolo = buscar_texto(
            protocolo,
            "nfe:nProt"
        )

        data_protocolo = buscar_texto(
            protocolo,
            "nfe:dhRecbto"
        )

    else:

        cstat = ""
        motivo = ""
        numero_protocolo = ""
        data_protocolo = ""

    return {
        "tipo": "NFCE",
        "arquivo": caminho.name,
        "chave": chave,
        "numero": numero,
        "serie": serie,
        "modelo": modelo,
        "data_emissao": formatar_data(data_emissao),

        "cnpj": cnpj,
        "cnpj_formatado": formatar_cnpj(cnpj),

        "emitente": emitente,
        "fantasia": fantasia,

        "valor": float(valor),

        "protocolo": numero_protocolo,
        "data_protocolo": formatar_data(data_protocolo),

        "cstat": cstat,
        "motivo": motivo,

        "status": definir_status(cstat),

        "erro": ""
    }


def ler_evento_cancelamento(root, caminho):
    """
    Procura eventos fiscais relacionados à NFC-e.

    110111 = Cancelamento
    """

    inf_evento = root.find(
        ".//nfe:infEvento",
        NAMESPACE
    )

    if inf_evento is None:
        return None

    chave = buscar_texto(
        inf_evento,
        "nfe:chNFe"
    )

    tipo_evento = buscar_texto(
        inf_evento,
        "nfe:tpEvento"
    )

    data_evento = buscar_texto(
        inf_evento,
        "nfe:dhEvento"
    )

    # Informações retornadas pela SEFAZ
    ret_evento = root.find(
        ".//nfe:retEvento/nfe:infEvento",
        NAMESPACE
    )

    if ret_evento is not None:

        cstat = buscar_texto(
            ret_evento,
            "nfe:cStat"
        )

        motivo = buscar_texto(
            ret_evento,
            "nfe:xMotivo"
        )

        protocolo = buscar_texto(
            ret_evento,
            "nfe:nProt"
        )

    else:

        cstat = ""
        motivo = ""
        protocolo = ""

    # 135 = Evento registrado e vinculado à NF-e
    # 136 = Evento registrado, mas não vinculado
    cancelamento_confirmado = (
        tipo_evento == "110111"
        and cstat in ("135", "136", "155")
    )

    return {
        "tipo": "EVENTO",
        "arquivo": caminho.name,
        "chave": chave,
        "tipo_evento": tipo_evento,
        "data_evento": formatar_data(data_evento),
        "cstat": cstat,
        "motivo": motivo,
        "protocolo": protocolo,
        "cancelamento_confirmado": cancelamento_confirmado,
        "erro": ""
    }


def ler_xml(caminho_xml):

    caminho = Path(caminho_xml)

    try:

        tree = ET.parse(caminho)
        root = tree.getroot()

        # Primeiro verifica se é uma NFC-e
        nfce = ler_nfce(root, caminho)

        if nfce:
            return nfce

        # Depois verifica se é XML de evento
        evento = ler_evento_cancelamento(
            root,
            caminho
        )

        if evento:
            return evento

        return {
            "tipo": "DESCONHECIDO",
            "arquivo": caminho.name,
            "status": "XML NÃO RECONHECIDO",
            "erro": "Não foi possível identificar NF-e/NFC-e ou evento."
        }

    except ET.ParseError as erro:

        return {
            "tipo": "ERRO",
            "arquivo": caminho.name,
            "status": "XML INVÁLIDO",
            "erro": str(erro)
        }

    except Exception as erro:

        return {
            "tipo": "ERRO",
            "arquivo": caminho.name,
            "status": "ERRO",
            "erro": str(erro)
        }