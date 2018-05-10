if(process.env.NODE_ENV != 'production'){
  require('dotenv').config();
}

module.exports.BOT_TOKEN = process.env.BOT_TOKEN
module.exports.WEBHOOK_URL = process.env.WEBHOOK_URL
module.exports.HOST = process.env.HOST
module.exports.PORT = process.env.PORT
module.exports.REJECTION_DELAY = process.env.REJECTION_DELAY
