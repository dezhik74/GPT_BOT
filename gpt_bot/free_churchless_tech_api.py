# Это через халявный API

# FREE_OPENAI_API_URL = 'https://free.churchless.tech/v1/chat/completions'
# @dp.message_handler()
# async def echo(message: types.Message):
#     data.messages.append(GPTMessage(role='user', content=message.text))
#     headers = {'Content-Type': 'application/json'}
#     msg = await message.answer(f"🔎 Идет генерация, подождите... \nДиалог состоит из {count_symbols(data)} символов")
#     print(f'data={asdict(data)}')
#     async with aiohttp.ClientSession() as session:
#         async with session.post(config.FREE_OPENAI_API_URL, headers=headers, json=asdict(data)) as resp:
#             print(resp.status)
#             json = await resp.json()
#             # print(json['choices'][0]['message']['content'])
#             pprint.pp(json)
#             data.messages.append(
#                 GPTMessage(role=json['choices'][0]['message']['role'],
#                            content=json['choices'][0]['message']['content']))
#             await message.answer(json["choices"][0]["message"]["content"])