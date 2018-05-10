const fs = require('fs');
const youtubedl = require('youtube-dl');
const path = require('path');

downloadVideoAsMP3 = (url) => {
  return new Promise((resolve, reject) => {
    console.log(url)
    youtubedl.getInfo(url, [], function(err, info) {
      if(err){
        reject(err)
        return;
      }
      const outputPath = path.join(__dirname, '..', 'audio')
      const filename = `${file.title}.%(ext)s`
      console.log('Downloading video...')
      youtubedl.exec(url, ['-x', '--audio-format', 'mp3', '--restrict-filenames','--output', path.join(outputPath, filename)], {}, function exec(err, output) {
        if(err){
          reject(err)
          return;
        }

        fs.readFile(path.join(outputPath, `${info.title}.mp3`, (err, data) => {
          if(err){
            reject(err)
            return;
          }
          resolve({
            title: `${info.title}`,
            data,
          })
        })
      })
    })
  })
  
}


module.exports = {
  downloadVideoAsMP3,
}
