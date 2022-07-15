brands = ['Vinataba', 'Phillip Morris', 'British America Tobacco', 'Tổng công ty thuốc lá Việt Nam',
          'Thuốc lá Thăng Long', 'Thuốc lá Sài Gòn', "Phillip Morris International", 'PMI', 'Phillip Morris Việt Nam',
          'BAT']

intents = ['ủng hộ', 'tài trợ', 'xây dựng', 'hỗ trợ']

# keywords = [
#     {
#         'keyword':
#             [[brand, intent] for intent in intents]
#         ,
#         'brand': brand,
#         'type': 'vi pham'
#     } for brand in brands]

type = []

keywords = [[brand, intent] for brand in brands for intent in intents]
