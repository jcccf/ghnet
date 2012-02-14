$ = require('jquery')
request = require('request')
events = require('events')
jsdom = require('jsdom')
mysql = require('mysql')

db = mysql.createClient {
  hostname: 'localhost',
  user: 'ghnet',
  password: 'ghnet87',
  database: 'ghnet'
}

req = request "https://github.com/explore", (error, response, body) ->
  throw error if error and response.statusCode isnt 200
  jsdom.env { html: body, scripts: [ 'http://code.jquery.com/jquery-1.7.1.min.js' ] }, (err, window) ->
    $ = window.jQuery
    $('.trending-repositories .ranked-repositories li h3').each ->
      url = $(this).find('a:last').attr('href')
      console.log url
      db.query('INSERT INTO trending (glogin, gname, url, rtype) VALUES(?,?,?,?)',
        [url.split("/")[1], url.split("/")[2], url, 'trending'], (error, info) ->
          console.log error.message if error) 
    $('.explore .main').children('.ranked-repositories').find('li h3').each ->
      url = $(this).find('a:last').attr('href')
      console.log url
      db.query('INSERT INTO trending (glogin, gname, url, rtype) VALUES(?,?,?,?)',
        [url.split("/")[1], url.split("/")[2], url, 'featured'], (error, info) ->
          console.log error.message if error)

setTimeout (-> process.exit(code=0)), 5000 # End after 5 seconds (hopefully nothing fails)