# Чат-бот - оповещение о проверке задания

## Учебный проект на онлайн-курсе DevMan

### Как установить

Python3 должен быть уже установлен.

Для установки зависимостей:
```
pip install -r requirements.txt
```
Создайте бот в телеграм, для этого 
- Напишите боту [@BotFather](https://t.me/BotFather) команду ```/newbot```
- Задайте имя бота:
```
- Первое — (можно на русском) как он будет отображаться в списке контактов
- Второе — (латинскими буквами) имя, по которому бота можно будет найти в поиске, 
-- Второе имя должно заканчиваться на _bot 
```
Для запуска в корне проекта нужно создать файл .env со следующим содержимым:
```
NOTIFIER_BOT_TOKEN=<Токен вашего телеграм-бота>
DEVMAN_TOKEN=<Токен для доступа к API DevMan>
ALLOWED_CHAT_ID=<id вашего чата в телеграм>
```
Узнать ID можно здесь: [https://t.me/userinfobot](https://t.me/userinfobot)

Создайте еще одного бота (аналогично первому) - для отправки логов ошибок.
В файл .env добавьте ещё одну переменную:
```
LOGGER_BOT_TOKEN=<Токен вашего телеграм-бота-логгера>
```
### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [https://dvmn.org/](https://dvmn.org/referrals/B9ehIJNk0dwuMb4b8mm7HqIdHWjUo816kuCaKCHI/)
