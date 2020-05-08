const express = require('express');
const router = express.Router();

const { Client } = require('@elastic/elasticsearch')
const client = new Client({ node: 'http://localhost:9200' })
// const bonsai_url    = process.env.BONSAI_URL;
// const elasticsearch = require('elasticsearch');
// const client        = new elasticsearch.Client({
//                             host: bonsai_url,
//                             log: 'trace'
//                         });
const request = require('request');
const natural = require('natural');

/* GET home page. */
router.get('/oldindex', (req, res) =>
{
  res.render('index', { title: 'Home'});
});

/* GET home page. */
router.get('/', (req, res) =>
{
  res.render('home', { title: 'Home'});
});

/* POST search ==> renders result page. */
router.post('/search', (req, res) =>
{
  const incQuerTxt = natural.PorterStemmer.stem(`${req.body.txtQuery}`);
  console.log("Lemmatisation Result: ", incQuerTxt);
  // txtQuery is the key for request query. (i.e.: txtQuery:"pixel3xl")

  // const tmpURL = `http://localhost:9200/_all/_search?q=*:${incQuerTxt}`
  // const tmpURL = `http://localhost:9080/astest?q=*:${incQuerTxt}` // for hitting back-end server

  request(tmpURL,  (error, response, body) => 
  {
    console.log(body.length)
    console.log(JSON.parse(body).took);
    const result = JSON.parse(body); // converts JSON string into JS Object.
    // res.json(result.hits.hits);
    
    // console.error('error:', error); // Print the error if one occurred
    // console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
    // console.log('body:', result); // Print the response from the request

    const toValues = result.hits.hits;
  
    if(((result.hits.hits[0])._type) == "products")
    {
      res.render('table',
      {
        title: 'Results',
        tableType: "Product",
        indexLoadTime: result.took,
        tmpObj: toValues
       });
    }
    else if(((result.hits.hits[0])._type) == "customers")
    {
      res.render('oldtable',
      {
        title: 'Results',
        tableType: "Customer",
        indexLoadTime: result.took,
        tmpObj: toValues
       });
    }

    // res.json(result);
  });
});

module.exports = router;

// curl -XGET "http://localhost:9200/_all/_search?q=*:scott"


// NLP STUFF TO LOOK INTO:
// https://github.com/winkjs/wink-lemmatizer => for lemma
// https://www.npmjs.com/package/natural => for nlp

// async function run (queryIn)
// {
//   const { body } = await client.search({
//     index: '*', // searching against all indexes
//     body: {
//       query: {
//         "multi_match" : {
//           "query":    queryIn,
//           "fields": ["customer_*",  "product_*"] // searching against all fields within each document
//         }
//       }
//     }
//   })
//   res.json(body.hits.hits);
// }
// run(incQuerTxt).catch(console.log)

