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
REDIRECT_BASE_URL = "" # this one is used for attaching base url for /problems/xxx
NODE_SERVER_BASE_URL = "" # your node server
LLM_API_KEY = "" # poe api key
LLM_COST_THRESHOLD = # max total cost for this run. If reached, disable LLM service
LLM_API_NUM_TRIES = # retry number if no proper response received 
BOT_NAME='{"rp": "your_roleplay_bot_name_in_poe","solver": "your_solver_bot_name_in_poe"}'
COST_PER_QUERY='{"rp": number_of_rp_cost,"solver": number_of_solver_cost}'
```
## Documentation

See [Docs](https://nonebot.dev/)
