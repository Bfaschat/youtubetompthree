const express = require('express');
const bodyParser = require('body-parser');
const config = require('./config/config')

const telegram = require('./routes/telegram.js');

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

app.use(`/bot${config.BOT_TOKEN}`, telegram)

app.listen(config.PORT, config.HOST, () => {
  console.log(`Express server is listening on http://${config.HOST}:${config.PORT}`);
});
