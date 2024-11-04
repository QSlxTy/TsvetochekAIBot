from handlers.user import start, support, tariff, photo, phone, answers, my_colors


def register_user_handler(dp):
    start.register_start_handler(dp)
    support.register_handler(dp)
    tariff.register_handler(dp)
    photo.register_handler(dp)
    phone.register_handler(dp)
    answers.register_handler(dp)
    my_colors.register_handler(dp)
