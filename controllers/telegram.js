const TelegramBot = require('node-telegram-bot-api');
const config = require('../config/config')
const youtube = require('../utils/youtubedl');
const fs = require('fs');
const path = require('path')

const sendConvertedVideo = (chatId, messageId, title, audio) => {
  console.log(title)
  bot.sendAudio(chatId, audio, {
    title: title
  })
  .then(response => {
    bot.deleteMessage(chatId, messageId)
    .catch(error => {
      console.log(error.response.body)
    })
  })
}

const isYoutubeLink = (text) => {
  const holyGrail = /(http|https):\/\/(www.)?(youtu\.be|youtube\.com\/watch)/g
    const results = text.match(holyGrail)
    if(results){
      return true
    }
    return false 
}

const bot = new TelegramBot(config.BOT_TOKEN);

bot.setWebHook(`${config.WEBHOOK_URL}/bot${config.BOT_TOKEN}`);

bot.on('channel_post', msg => {
  console.log(msg)
  if(isYoutubeLink(msg.text)){
    youtube.downloadVideoAsMP3(msg.text)
    .then(audio => {
      sendConvertedVideo(msg.chat.id, msg.message_id, audio.title, audio.data)
    })
    .catch(error => {
      console.log(error)
    })
  }
});

let removalDelay;

bot.on('callback_query', query => {
  // If the user clicking the action is the same who made the message
  if(query.from.id === query.message.reply_to_message.from.id){
    clearInterval(removalDelay)

    if(query.data === 'publish_update'){
      youtube.downloadVideoAsMP3(query.message.reply_to_message.text)
      .then(audio => {
        sendConvertedVideo(
          query.message.reply_to_message.chat.id,
          query.message.reply_to_message.message_id,
          audio.title,
          audio.data)
      })
      .catch(error => {
        console.log(error)
      })
      bot.answerCallbackQuery({
        callback_query_id: query.id
      })
    }

    bot.deleteMessage(query.message.chat.id, query.message.message_id)
  }
});

bot.on('text', async (msg) => {
  if(isYoutubeLink(msg.text)){
    const message = await bot.sendMessage(msg.chat.id, "URL detected. Do you want me to publish this on your Twitter feed? This message will dissapear in 5 seconds", {
      reply_to_message_id: msg.message_id,
      reply_markup: {
        inline_keyboard: [[{
          text: 'Yes',
          callback_data: 'publish_update'
        }]]
      }
    })

    removalDelay = setInterval(() => {
      bot.deleteMessage(message.chat.id, message.message_id)
      clearInterval(removalDelay)
    }, config.REJECTION_DELAY)
  }
})

module.exports = {
  bot,
  sendConvertedVideo,
}