# koku
Our own crypto-currency made in Python/OpenCL!

You can see the client options with

```shell
./client.py --help
```

First, you will need to generate a key with the command

```shell
./client --key
```

This will generate .Koku.pem file. Don't lose it otherwise you won't be able to spend the money sent to this key.
This command will also prompt your address, you can find it again at any moment with

```shell
./client --address
```
