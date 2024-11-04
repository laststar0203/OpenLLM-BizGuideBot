
만약 poetry install -vvv 했는데 Using keyring backend 'SecretService Keyring' 메시지가 뜨면서 무한 행이 걸린다면
아래 명령어를 수행하시오.
 
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
