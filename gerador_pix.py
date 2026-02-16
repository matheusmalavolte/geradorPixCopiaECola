import qrcode
import base64
import os
from io import BytesIO


class PixEstatico:
    def __init__(self, chave, nome_recebedor, cidade_recebedor="SERRA"):
        self.chave = chave
        self.nome_recebedor = nome_recebedor
        self.cidade_recebedor = cidade_recebedor


    # CRC16 padrão BACEN

    def crc16(self, payload: str) -> str:
        polinomio = 0x1021
        resultado = 0xFFFF

        for char in payload:
            resultado ^= ord(char) << 8
            for _ in range(8):
                if resultado & 0x8000:
                    resultado = (resultado << 1) ^ polinomio
                else:
                    resultado <<= 1
                resultado &= 0xFFFF

        return f"{resultado:04X}"

    def _campo(self, id: str, valor: str) -> str:
        return f"{id}{len(valor):02d}{valor}"


    # Payload PIX ESTÁTICO

    def gerar_payload(self, valor: float) -> str:
        merchant_account = (
            self._campo("00", "BR.GOV.BCB.PIX") +
            self._campo("01", self.chave)
        )

        payload = (
            "000201"
            "010211"  # PIX ESTÁTICO
            + self._campo("26", merchant_account)
            + "52040000"
            + "5303986"
            + self._campo("54", f"{valor:.2f}")
            + "5802BR"
            + self._campo("59", self.nome_recebedor[:25])
            + self._campo("60", self.cidade_recebedor[:15])
            + "6304"
        )

        return payload + self.crc16(payload)


    # QR Code Base64

    def gerar_qrcode_base64(self, payload: str) -> str:
        img = qrcode.make(payload)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


    # Função principal

    def gerar_pix(self, valor: float):
        payload = self.gerar_payload(valor)
        qrcode_base64 = self.gerar_qrcode_base64(payload)

        return {
            "payload": payload,
            "qrcode_base64": qrcode_base64
        }



# TESTE REAL

if __name__ == "__main__":
    pix = PixEstatico(
        chave="10679733701",  # CPF / chave PIX
        nome_recebedor="MATHEUS MALAVOLTE"
    )

    resultado = pix.gerar_pix(1.00)

    print("\nPIX COPIA E COLA:")
    print(resultado["payload"])

    #  Gerar e salvar QR Code
    #  Gerar e salvar QR Code com ID automático

    # Verificar arquivos existentes
    arquivos_existentes = [f for f in os.listdir() if f.startswith("pix_") and f.endswith(".png")]

    ids = []
    for arquivo in arquivos_existentes:
        try:
            numero = int(arquivo.replace("pix_", "").replace(".png", ""))
            ids.append(numero)
        except:
            pass

    proximo_id = max(ids) + 1 if ids else 1

    nome_arquivo = f"pix_{proximo_id}.png"

    img = qrcode.make(resultado["payload"])
    img.save(nome_arquivo)

    print(f"\nQR Code salvo como {nome_arquivo}")
