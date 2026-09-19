from cryptography.hazmat.primitives.serialization import pkcs12


def carregar_certificado_pfx(caminho_pfx, senha):
    """
    Carrega um certificado digital A1 (.pfx/.p12).

    O certificado e a chave privada permanecem
    somente na memória durante esta validação.
    """

    with open(caminho_pfx, "rb") as arquivo:
        dados_pfx = arquivo.read()

    senha_bytes = senha.encode("utf-8") if senha else None

    chave_privada, certificado, certificados_adicionais = (
        pkcs12.load_key_and_certificates(
            dados_pfx,
            senha_bytes
        )
    )

    if certificado is None:
        raise ValueError(
            "Nenhum certificado foi encontrado no arquivo PFX."
        )

    if chave_privada is None:
        raise ValueError(
            "Nenhuma chave privada foi encontrada no arquivo PFX."
        )

    return {
        "certificado": certificado,
        "chave_privada": chave_privada,
        "cadeia": certificados_adicionais or []
    }


def obter_informacoes_certificado(caminho_pfx, senha):
    dados = carregar_certificado_pfx(
        caminho_pfx,
        senha
    )

    certificado = dados["certificado"]

    return {
        "titular": certificado.subject.rfc4514_string(),
        "emissor": certificado.issuer.rfc4514_string(),
        "numero_serie": str(certificado.serial_number),
        "valido_de": certificado.not_valid_before_utc,
        "valido_ate": certificado.not_valid_after_utc
    }