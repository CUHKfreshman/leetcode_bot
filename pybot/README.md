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
6. Fill in .env.{your_env} for your production & dev respectively.
```
LOG_LEVEL = ...
REDIRECT_BASE_URL = ""
NODE_SERVER_BASE_URL = ""
LLM_API_KEY = ""
LLM_COST_THRESHOLD = # max cost for this run
LLM_API_NUM_TRIES = # retry number if no proper response received 
RP_BOT_NAME = ""
RP_BOT_COST_PER_QUERY = # cost per query
SOLVER_BOT_NAME = ""
SOLVER_BOT_COST_PER_QUERY = # cost per query
```
## Documentation

See [Docs](https://nonebot.dev/)
