# pybot

## How to start

1. generate project using `nb create` .
2. create your plugin using `nb plugin create` .
3. writing your plugins under `src/plugins` folder.
4. run your bot using `nb run --reload` .
5. Use template in .env as per you need:
```
ENVIRONMENT=dev
DRIVER=~httpx+~websockets
QQ_IS_SANDBOX=false
COMMAND_START=["/",""]
QQ_BOTS='[
    {
        "id":"",
        "token":"",
        "secret":"",
        "intent":{
        "c2c_group_at_messages":true
        } 
    }
]'
```
## Documentation

See [Docs](https://nonebot.dev/)
