const express = require('express');
const helmet = require('helmet');
const bodyParser = require('body-parser');
const childProc = require('child_process');
const compression = require('compression');
const logger = require('morgan');
const globalLog = require('global-request-logger');
const app = express();

globalLog.initialize(); // for logging outgoing GET requests

// globalLog.on('success', (request, response) =>
// {
//   console.log('SUCCESS');
//   console.log('Request', request);
//   console.log('Response', response);
// });

app.use(helmet());
app.use(compression());

const port = process.env.port || 8080; 

app.use(bodyParser.json()); // parse incoming requests
app.use(bodyParser.urlencoded({ extended: false }));

app.use(logger('dev'));
app.set('port', (process.env.PORT || 8080));
app.use(express.static(__dirname + '/public'));

app.set('view engine', 'pug'); // engine - pug
app.set('views', __dirname + '/views');

const routes = require('./routes/index'); // include routes
app.use('/', routes);

// catch 404 then forward to error handler
app.use((req, res, next) =>
{
  let err = new Error('404, File Not Found');
  err.status = 404;
  next(err);
});

// last app.use callback
app.use((err, req, res) =>
{
  res.status(err.status || 500);
  res.render('error', {
    message: err.message,
    error: {}
  });
});

app.listen(app.get('port'), () =>
{
  console.log(`app is running on http://localhost:${port}`);
});