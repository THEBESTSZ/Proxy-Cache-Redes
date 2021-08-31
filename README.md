 ------------------------------------------------------------------------------------------
    Alunos:        William Felipe Tsubota          - 2017.1904.056-7
                   Marllon Lucas Rodrigues Rosa    - 2017.1904.045-1
                   Gabriel C. M.                   - 2017.1904.005-2
                               
                              Trabalho 1
    
    Professora:    Hana Karina Salles Rubinsztejn
------------------------------------------------------------------------------------------

Proxy HTTP

Este projeto visa a criação de um servidor proxy com as funcionalidades de receber uma requisição
do navegar e armazenar os dados da requisição

Relatório redes:

1.1 - Cache: Foi implementado um dicionário para armazenagem da cache, tal dicionário é composto pela chave (url completa da requisição) e o valor é uma lista com os replies. Um scheduler é lançado para cada cache armazenada em um tempo de 5 minutos, após esse tempo tal chave e seu valor é apagado do dicionário. Caso a cache esteja cheia (Há uma variável simulando o tamanho da cache) é retirado da cache o elemento mais antigo e verificado se com o novo valor do tamanho da cache é possível inserir a nova informação na cache. OBS: A partir no python 3.7 o dicionário mantém a ordem de inserção, e utilizamos esse fato na nossa política de substituição, ou seja, removemos os primeiros elementos do dicionário para alocar espaço.

1.2 - Blacklist: Todos os links a serem bloqueados devem ser colocados em "blacklist.txt", separados por uma quebra de linha, a implementação deste é intuitiva, apenas comparamos se o link que estamos requisitando acesso está na blacklist.

2.1 - Lista de implementações
* Cache - implementado
* blacklist - implementado
* multiplos clientes - checked
* conexão - tcp - checked
* porta não definida - checked
* logs - checked (obs os logs são criados a cada 30 segundos, apenas se houver acesso à sites neste tempo)

2.2 - Lista de extras implementados:
* bloqueio por horário

Para execução da proxy basta executar: python3 proxy.py
