# from bit import PrivateKey
#
# # # Приватный ключ из wif
# my_key = PrivateKey(wif='Ky5FW97njq5ytJV12fifvMiQ2TAeMbBULqaY4RFDfPVphDvKx9MF')
# #
# # # Количество долларов перевода, можно поменять на btc
# # money = 0.00009889 - 0.00000111
# #
# # # Кошелек куда будут переведены деньги
# # wallet = 'bc1q04p7gp2cz3stkge2t5mqf22eydj2jl345mrqun'
# #
# # # Коммисия перевода, если поставить слишком маленькую, то транзакцию не примут
# # # И чем больше коммисия, тем быстрее пройдет перевод
# # fee = 0.00000111
# #
# # # Генерация транзакции
# # tx_hash = my_key.create_transaction([(wallet, money, 'btc')], fee=fee, absolute_fee=True)
# #
# # print(tx_hash)
#
# import requests
#
# # Адрес кошелька пользователя
# wallet = '18atgMmW9rA7dPv4HygL76Db8T1tvMcGCR'
# # wallet = gen_address(0)
#
# url = f'https://blockchain.info/rawaddr/{wallet}'
# x = requests.get(url)
# wallet = x.json()
#
# print('Итоговый баланс:'+str(wallet['final_balance']))
# print('Транзакции:'+str(wallet['txs']))
#
# if wallet['total_received'] == 0:
#     print('баланс пустой')
#
#
# from bipwallet.utils import *
#
# from bipwallet import wallet
#
# # generate 12 word mnemonic seed
# # seed = wallet.generate_mnemonic()
# #
# # print(seed)
#
# def gen_address(index):
#     pass
#     # Наша seed фраза
#     seed = 'debate train example fancy stumble accuse innocent recall casual ketchup gesture maid'
#
#     # Мастер ключ из seed фразы
#     master_key = HDPrivateKey.master_key_from_mnemonic(seed)
#     # print(master_key)
#
#     # Public key из мастер ключа по пути 'm/44/0/0/0'
#     root_keys = HDKey.from_path(master_key, "m/84'/0'/0'/0")[-1].public_key.to_b58check()
#     print(root_keys)
#
#     # Extended public key
#     # xpublic_key = str(root_keys, encoding="utf-8")
#     xpublic_key = root_keys
#
#     # Адрес дочернего кошелька в зависимости от значения index
#     address = Wallet.deserialize(xpublic_key, network='BTC').get_child(index, is_prime=False).to_address()
#     # print(address)
#
#     rootkeys_wif = HDKey.from_path(master_key, f"m/84'/0'/0'/0/{index}")[-1]
#
#     # Extended private key
#     # xprivatekey = str(rootkeys_wif.to_b58check(), encoding="utf-8")
#     xprivatekey = rootkeys_wif
#
#     # Wallet import format
#     # wif = Wallet.deserialize(xprivatekey, network='BTC').export_to_wif()
#
#     # return address, str(wif, 'utf-8')
#     return address
#
# # for i in range(999999999):
# #     if 'bc1qxr' in gen_address(i):
# #         print(i)
# #         break
# print(gen_address(0), gen_address(2000))
#
# # master_key = HDPrivateKey.master_key_from_mnemonic(seed)
# # # print(master_key)
# #
# # # Public key из мастер ключа по пути 'm/44/0/0/0'
# # root_keys = HDKey.from_path(master_key, "m/44'/0'/0'/0")[-1].public_key.to_b58check()
# # print(root_keys)
# # wif = Wallet.deserialize('xpub6Dx2g4WJhuKpAPEMmx2Tk5d9fD2j2bLjaQHk46F2WGbSBxpHNBk92c8Y3oEmWyJRroSQJ6eBBoDW9QB3UKFTCiBcboCodzfD1BsHGb3ACo1', network='BTC').export_to_wif()
# # print(wif)


from bit import PrivateKey, PrivateKeyTestnet

my_key = PrivateKey()

print(my_key.version)

print(my_key.to_wif())

print(my_key.address)

tx_hash = my_key.send([("mkH41dfD4S8DEoSfcVSvEfpyZ9siogWWtr", 1, "usd")])

print(tx_hash)
