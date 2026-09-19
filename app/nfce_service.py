import os
import tempfile
import xml.etree.ElementTree as ET

import requests
import truststore

from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, NoEncryption, pkcs12,
)

truststore.inject_into_ssl()

URL_CONSULTA_SVRS = (
    "https://nfce.svrs.rs.gov.br/"
    "ws/NfeConsulta/NfeConsulta4.asmx"
)
NAMESPACE_NFE = "http://www.portalfiscal.inf.br/nfe"
NAMESPACE_WSDL = (
    "http://www.portalfiscal.inf.br/"
    "nfe/wsdl/NFeConsultaProtocolo4"
)


def validar_chave(chave):
    chave = "".join(c for c in str(chave) if c.isdigit())
    if len(chave) != 44:
        raise ValueError("A chave da NFC-e precisa possuir 44 dígitos.")
    return chave


def extrair_pfx_temporariamente(caminho_pfx, senha):
    with open(caminho_pfx, "rb") as arquivo:
        dados_pfx = arquivo.read()

    senha_bytes = senha.encode("utf-8") if senha else None
    chave_privada, certificado, cadeia = pkcs12.load_key_and_certificates(
        dados_pfx, senha_bytes
    )
    if certificado is None:
        raise ValueError("Certificado não encontrado no PFX.")
    if chave_privada is None:
        raise ValueError("Chave privada não encontrada no PFX.")

    arq_cert = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    arq_chave = tempfile.NamedTemporaryFile(delete=False, suffix=".key")
    try:
        arq_cert.write(certificado.public_bytes(Encoding.PEM))
        if cadeia:
            for cert_cadeia in cadeia:
                arq_cert.write(cert_cadeia.public_bytes(Encoding.PEM))
        arq_chave.write(
            chave_privada.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption(),
            )
        )
    finally:
        arq_cert.close()
        arq_chave.close()
    return arq_cert.name, arq_chave.name


def montar_xml_consulta(chave):
    return (
        '<consSitNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">'
        "<tpAmb>1</tpAmb><xServ>CONSULTAR</xServ>"
        f"<chNFe>{chave}</chNFe></consSitNFe>"
    )


def montar_envelope_soap(xml_consulta):
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">'
        '<soap12:Body>'
        f'<nfeDadosMsg xmlns="{NAMESPACE_WSDL}">{xml_consulta}</nfeDadosMsg>'
        '</soap12:Body></soap12:Envelope>'
    )


def _texto(elemento, nome):
    if elemento is None:
        return ""
    achado = elemento.find(f".//{{{NAMESPACE_NFE}}}{nome}")
    if achado is not None and achado.text:
        return achado.text.strip()
    return ""


def interpretar_resposta(xml_resposta):
    try:
        root = ET.fromstring(xml_resposta)
    except ET.ParseError as erro:
        raise ValueError(f"Resposta da SEFAZ não contém XML válido: {erro}")

    ret = root.find(f".//{{{NAMESPACE_NFE}}}retConsSitNFe")
    if ret is None:
        return {
            "sucesso": False, "status": "RESPOSTA DESCONHECIDA",
            "cstat": "", "motivo": "retConsSitNFe não encontrado.",
            "protocolo": "", "data_recebimento": "", "chave": "",
            "eventos": [], "xml_resposta": xml_resposta,
        }

    cstat_consulta = _texto(ret, "cStat")
    motivo_consulta = _texto(ret, "xMotivo")
    chave = _texto(ret, "chNFe")

    inf_prot = ret.find(
        f".//{{{NAMESPACE_NFE}}}protNFe/{{{NAMESPACE_NFE}}}infProt"
    )
    cstat_prot = _texto(inf_prot, "cStat")
    motivo_prot = _texto(inf_prot, "xMotivo")
    protocolo = _texto(inf_prot, "nProt")
    data_recebimento = _texto(inf_prot, "dhRecbto")

    eventos = []
    cancelada = False
    for proc in ret.findall(f".//{{{NAMESPACE_NFE}}}procEventoNFe"):
        envio = proc.find(
            f".//{{{NAMESPACE_NFE}}}evento/{{{NAMESPACE_NFE}}}infEvento"
        )
        retorno = proc.find(
            f".//{{{NAMESPACE_NFE}}}retEvento/{{{NAMESPACE_NFE}}}infEvento"
        )
        tipo = _texto(envio, "tpEvento")
        cstat_evento = _texto(retorno, "cStat")
        evento = {
            "tipo_evento": tipo,
            "descricao": _texto(envio, "descEvento"),
            "cstat": cstat_evento,
            "motivo": _texto(retorno, "xMotivo"),
            "protocolo": _texto(retorno, "nProt"),
            "data": _texto(retorno, "dhRegEvento") or _texto(envio, "dhEvento"),
        }
        eventos.append(evento)
        # 110111 = cancelamento. cStat 135 = evento vinculado à nota.
        # 136 não é considerado confirmação automática de cancelamento.
        if tipo == "110111" and cstat_evento == "135":
            cancelada = True

    if cancelada:
        status = "CANCELADA"
    elif cstat_consulta == "217":
        status = "NÃO CONSTA"
    elif cstat_prot in ("100", "150") or cstat_consulta == "100":
        status = "AUTORIZADA"
    elif cstat_prot == "110":
        status = "DENEGADA"
    else:
        status = "OUTRO"

    motivo = motivo_prot or motivo_consulta
    if cancelada:
        for evento in eventos:
            if evento["tipo_evento"] == "110111" and evento["cstat"] == "135":
                motivo = evento["motivo"] or "Cancelamento registrado e vinculado."
                break

    return {
        "sucesso": bool(cstat_consulta),
        "status": status,
        "cstat": cstat_consulta,
        "cstat_protocolo": cstat_prot,
        "motivo": motivo,
        "motivo_consulta": motivo_consulta,
        "protocolo": protocolo,
        "data_recebimento": data_recebimento,
        "chave": chave,
        "eventos": eventos,
        "xml_resposta": xml_resposta,
    }


def consultar_nfce(chave, caminho_pfx, senha, timeout=30):
    chave = validar_chave(chave)
    if not caminho_pfx or not os.path.isfile(caminho_pfx):
        raise FileNotFoundError("Certificado PFX não encontrado.")

    cert_temp = chave_temp = None
    try:
        cert_temp, chave_temp = extrair_pfx_temporariamente(caminho_pfx, senha)
        envelope = montar_envelope_soap(montar_xml_consulta(chave))
        soap_action = (
            "http://www.portalfiscal.inf.br/"
            "nfe/wsdl/NFeConsultaProtocolo4/nfeConsultaNF"
        )
        headers = {
            "Content-Type": (
                'application/soap+xml; charset=utf-8; '
                f'action="{soap_action}"'
            ),
            "Accept": "application/soap+xml, application/xml, text/xml",
            "User-Agent": "Verificador-NFCe/1.0",
        }
        resposta = requests.post(
            URL_CONSULTA_SVRS,
            data=envelope.encode("utf-8"),
            headers=headers,
            cert=(cert_temp, chave_temp),
            timeout=timeout,
        )
        if resposta.status_code != 200:
            raise RuntimeError(
                f"Erro HTTP retornado pela SEFAZ: {resposta.status_code}\n\n"
                f"{resposta.text[:2000]}"
            )
        return interpretar_resposta(resposta.text)
    finally:
        for caminho in (cert_temp, chave_temp):
            if caminho:
                try:
                    os.remove(caminho)
                except OSError:
                    pass
