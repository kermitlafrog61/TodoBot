import logging

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from core.settings import settings
from core.utils import db, db_connection
from todo.models import Todo
from todo.queries import (create_todo, destroy_todo, list_todos, retrieve_todo,
                          update_todo)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


ENTER_TITLE = 0
ENTER_DESCRIPTION = 1
ENTER_DUE_DATE = 2


@db
def create_tables():
    db_connection.create_tables([Todo], safe=True)


def get_todo_text(**kwargs):
    text = ''
    for key, value in kwargs.items():
        text += f'{key}: {value}\n'
    return text


async def start(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello, I'm a todo bot\nCredits: @kermit_la_frog",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton('All todos')],
            [KeyboardButton('Create todo')]
        ])
    )


async def list(update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('List')
    todos = list_todos()
    for todo in todos:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "More", callback_data=f'retrieve-{todo.id}')],
        ])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_todo_text(**todo.dict()),
            reply_markup=keyboard
        )


async def create(update, context):
    logger.info('Create')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Enter todo title'
    )
    return ENTER_TITLE


async def complete_create(update, context):
    todo = create_todo(update.message.text)
    await retrieve(update, context, todo.id)
    return ConversationHandler.END


async def retrieve(update, context, todo_id=None):
    if todo_id:
        action = 'retrieve'
        id = todo_id
    else:
        action, id = update.callback_query.data.split('-')
    if action == 'retrieve':
        logger.info('Retrieve')
        todo = retrieve_todo(id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Edit Description", callback_data=f'description-{id}')],
            [InlineKeyboardButton(
                "Edit Completed", callback_data=f'check-{id}')],
            [InlineKeyboardButton("Edit Due", callback_data=f'due-{id}')],
            [InlineKeyboardButton("Delete", callback_data=f'delete-{id}')],
        ])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_todo_text(**todo.dict()),
            reply_markup=keyboard
        )


async def update_description(update, context):
    logger.info('Description')
    action, id = update.callback_query.data.split('-')
    if action == 'description':
        context.user_data['id'] = id
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Enter new description'
        )
        return ENTER_DESCRIPTION


async def handle_description(update, context):
    id = context.user_data['id']
    update_todo(id, 'description', update.message.text)
    await retrieve(update, context, id)
    context.user_data.clear()
    return ConversationHandler.END


async def update_due_date(update, context):
    logger.info('Due')
    action, id = update.callback_query.data.split('-')
    context.user_data['id'] = id
    if action == 'due':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Enter new due date in format YYYY-MM-DD'
        )
        return ENTER_DUE_DATE


async def handle_due_date(update, context):
    id = context.user_data['id']
    update_todo(id, 'due_to', update.message.text)
    await retrieve(update, context, id)
    context.user_data.clear()
    return ConversationHandler.END


async def update_completed(update, context):
    logger.info('Completed')
    action, id = update.callback_query.data.split('-')
    if action == 'check':
        update_todo(id, 'completed', True)
        await retrieve(update, context, id)


async def delete(update, context):
    logger.info('Delete')
    action, id = update.callback_query.data.split('-')
    if action == 'delete':
        destroy_todo(id)
        await list(update, context)


if __name__ == '__main__':
    create_tables()
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    create_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text(['Create todo']), create),
            CommandHandler('create', create),
        ],
        states={
            ENTER_TITLE: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, complete_create)]
        },
        fallbacks=[],
    )

    description_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            update_description, pattern='description-*')],
        states={
            ENTER_DESCRIPTION: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_description)],
        },
        fallbacks=[],
    )

    due_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(update_due_date, pattern='due-*')],
        states={
            ENTER_DUE_DATE: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_due_date)],
        },
        fallbacks=[],
    )

    app.add_handlers([
        CommandHandler('start', start),
        CommandHandler('list', list),
        MessageHandler(filters.Text(['All todos']), list),
        CallbackQueryHandler(retrieve, pattern='retrieve-*'),
        CallbackQueryHandler(update_completed, pattern='check-*'),
        CallbackQueryHandler(delete, pattern='delete-*'),
        create_handler,
        description_handler,
        due_handler,
    ])

    app.run_polling()
