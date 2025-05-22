# Frigate to Google Drive Instant Uploader with MQTT (Suporte a Rclone)

Este é um script simples que envia clipes de eventos do Frigate para o Google Drive instantaneamente via MQTT, sem a necessidade de cronjobs.
A principal modificação é que o upload agora é feito utilizando o rclone, que facilita a integração com Google Drive, tornando o processo mais confiável e flexível.

O script usa um banco de dados SQLite para controlar quais eventos já foram enviados, garantindo que somente novos clipes sejam enviados. Em caso de erro, o upload é tentado novamente automaticamente.

Além disso, foi incluído um webhook para enviar mensagens a um canal Mattermost quando ocorrer algum erro, ajudando no monitoramento.

Funcionamento básico
O script fica "ouvindo" eventos novos do Frigate publicados via MQTT e faz o upload do clipe correspondente ao Google Drive em poucos segundos, utilizando o rclone para transferir os arquivos.

No meu ambiente de teste, uso Apache Mosquitto como broker MQTT, Frigate como NVR, e tudo isso rodando em containers LXC no Proxmox.

# Requisitos

Python 3.8 ou superior
Broker MQTT (exemplo: Apache Mosquitto)
Frigate configurado para publicar eventos MQTT
Rclone configurado para acesso ao Google Drive
Google Service Account com permissões no Google Drive (configurada no rclone)

# Exemplo de configuração MQTT do Frigate

```yaml
mqtt:
  host: 192.168.0.55
  user: username
  password: secret
  port: 1883
  topic_prefix: frigate
  client_id: frigate

# restante da configuração do Frigate
````

Você pode verificar se o MQTT está funcionando assinando o tópico `frigate/events` com um cliente MQTT, como MQTT Explorer ou mosquitto_sub. Se receber eventos, o script pode processá-los.

# Configuração do Rclone para Google Drive

Para evitar limitações e quotas padrão, é recomendável criar seu próprio Client ID e Client Secret para o Google Drive, seguindo a documentação oficial do rclone:

👉 https://rclone.org/drive/#making-your-own-client-id

Passos básicos:

Crie um projeto no Google Cloud Console.
Ative a API do Google Drive.
Configure as credenciais OAuth para obter Client ID e Client Secret.
Configure o rclone com esses dados, criando um remote do tipo drive.
Teste o rclone para garantir que está funcionando corretamente.

# Uso sem Docker

1. Clone este repositório.
2. Renomeie `env_example` para `.env` e ajuste as variáveis conforme seu ambiente.
3. Crie e ative um ambiente virtual Python:
4. `cd /root/frigate-gdrive-instant-uploader`
5. `python3 -m venv venv`
6. `source venv/bin/activate`
7. Instale as dependências:
8. `pip install -r requirements.txt`
9. Configure o rclone para Google Drive conforme explicado acima.
10. Execute o script com:
11. `python main.py`
    
# Uso com Docker

1. Clone este repositório.
2. Renomeie `env_example` para `.env` e configure conforme necessário.
3. Configure o rclone na imagem Docker (incluindo o arquivo de configuração do rclone no container).
4. Execute:
5. `docker compose up -d`
6. Verifique os logs com:
7. `docker logs frigate-gdrive-instant-uploader`
8. ou no arquivo /logs/app.log.
Considerações finais

Com a integração via rclone, o upload para Google Drive fica mais robusto, e você pode usar as facilidades do rclone, como cache, controle de banda, criptografia, entre outros.

Para mais informações sobre o rclone e Google Drive, consulte a documentação oficial:
https://rclone.org/drive/
