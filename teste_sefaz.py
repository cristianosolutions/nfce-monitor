from getpass import getpass
from pathlib import Path

from app.nfce_service import consultar_nfce


def main():
    print("=" * 70)
    print("CONSULTA DE NFC-e - SEFAZ / SVRS")
    print("=" * 70)

    chave = input(
        "\nChave da NFC-e: "
    ).strip()

    caminho_pfx = input(
        "Caminho do certificado PFX: "
    ).strip()

    caminho_pfx = (
        caminho_pfx
        .strip('"')
        .strip("'")
    )

    if not Path(caminho_pfx).exists():
        print(
            "\nERRO: Certificado PFX não encontrado."
        )
        return

    senha = getpass(
        "Senha do certificado: "
    )

    print()
    print("Consultando SEFAZ/SVRS...")
    print()

    try:
        resultado = consultar_nfce(
            chave=chave,
            caminho_pfx=caminho_pfx,
            senha=senha
        )

        print("=" * 70)
        print("RESULTADO DA CONSULTA")
        print("=" * 70)

        print(
            f"cStat: {resultado['cstat']}"
        )

        print(
            f"xMotivo: {resultado['motivo']}"
        )

        print(
            f"Status interpretado: {resultado['status']}"
        )

        print(
            f"Protocolo: {resultado['protocolo']}"
        )

        print(
            "Data recebimento: "
            f"{resultado['data_recebimento']}"
        )

        print("=" * 70)

    except Exception as erro:

        print("=" * 70)
        print("ERRO NA CONSULTA")
        print("=" * 70)

        print(
            type(erro).__name__
        )

        print(
            str(erro)
        )

        print("=" * 70)


if __name__ == "__main__":
    main()