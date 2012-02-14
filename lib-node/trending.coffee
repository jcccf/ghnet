$ = require('jquery')
request = require('request')
events = require('events')
jsdom = require('jsdom')
mysql = require('db-mysql')

db = new mysql.Database {
  hostname: 'localhost',
  user: 'ghnet',
  password: 'ghnet87',
  database: 'ghnet'
}

req = request "https://github.com/explore", (error, response, body) ->
  throw error if error and response.statusCode isnt 200
  jsdom.env { html: body, scripts: [ 'http://code.jquery.com/jquery-1.7.1.min.js' ] }, (err, window) ->
    $ = window.jQuery
    db.connect (error) ->
      thisdb = this
      throw error if error
      $('.trending-repositories .ranked-repositories li h3').each ->
        url = $(this).find('a:last').attr('href')
        console.log url
        thisdb.query().
        insert('trending', ['glogin', 'gname', 'url', 'rtype'], [url.split("/")[1], url.split("/")[2], url, 'trending']).
        execute (error, result) ->
          console.log error if error
      $('.explore .main').children('.ranked-repositories').find('li h3').each ->
        url = $(this).find('a:last').attr('href')
        console.log url
        thisdb.query().
        insert('trending', ['glogin', 'gname', 'url', 'rtype'], [url.split("/")[1], url.split("/")[2], url, 'featured']).
        execute (error, result) ->
          console.log error if error