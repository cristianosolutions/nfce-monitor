from getpass import getpass
from pathlib import Path

from app.certificado_service import obter_informacoes_certificado


def main():
    print("=" * 60)
    print("TESTE DO CERTIFICADO DIGITAL A1")
    print("=" * 60)

    caminho = input(
        "\nInforme o caminho completo do arquivo PFX: "
    ).strip()

    caminho = caminho.strip('"').strip("'")

    arquivo = Path(caminho)

    if not arquivo.exists():
        print("\nERRO: Arquivo não encontrado.")
        return

    if arquivo.suffix.lower() not in (".pfx", ".p12"):
        print("\nERRO: Selecione um certificado .pfx ou .p12.")
        return

    senha = getpass(
        "Digite a senha do certificado: "
    )

    try:
        informacoes = obter_informacoes_certificado(
            arquivo,
            senha
        )

        print()
        print("=" * 60)
        print("CERTIFICADO CARREGADO COM SUCESSO")
        print("=" * 60)

        print(
            f"Titular: {informacoes['titular']}"
        )

        print(
            f"Emissor: {informacoes['emissor']}"
        )

        print(
            f"Válido de: {informacoes['valido_de']}"
        )

        print(
            f"Válido até: {informacoes['valido_ate']}"
        )

        print("=" * 60)

    except Exception as erro:
        print()
        print("Não foi possível abrir o certificado.")
        print(f"Detalhes: {erro}")


if __name__ == "__main__":
    main()